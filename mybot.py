from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os
import re
from aiohttp import web


BOT_TOKEN = os.environ.get("BOT_TOKEN")
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")


# ------------------------------
#        START COMMAND
# ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["فروش روزانه", "حقوق"],
        ["برداشت", "موجودی صندوق"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("یک گزینه را انتخاب کنید:", reply_markup=reply_markup)


# ------------------------------
#   تغییر اعداد فارسی به انگلیسی
# ------------------------------
def convert_fa_numbers(text):
    fa = "۰۱۲۳۴۵۶۷۸۹"
    en = "0123456789"
    table = str.maketrans(fa, en)
    return text.translate(table)


# ------------------------------
#   پیام‌ها
# ------------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # حالت منتظر خرج‌کرد
    if context.user_data.get("state") == "WAIT_EXPENSE":

        raw = convert_fa_numbers(text)

        if "ریال" not in raw:
            await update.message.reply_text("❗ لطفاً مبلغ را همراه کلمه «ریال» بفرست.")
            return

        parts = raw.split("ریال")
        amount_text = parts[0].strip()
        after_amount = parts[1].strip()

        numbers = re.findall(r"\d+", amount_text)
        if not numbers:
            await update.message.reply_text("❗ مبلغ درست تشخیص داده نشد.")
            return

        amount = int(numbers[0])

        words = after_amount.split()

        if len(words) < 2:
            await update.message.reply_text("❗ لطفاً بعد از مبلغ، عنوان و حساب را بفرست.")
            return

        if len(words) >= 3:
            account = " ".join(words[-2:])
            title = " ".join(words[:-2])
        else:
            account = words[-1]
            title = " ".join(words[:-1])

        await update.message.reply_text(
            f"✔ ثبت شد\n\nمبلغ: {amount}\nعنوان: {title}\nحساب: {account}",
            reply_markup=ReplyKeyboardRemove(),
        )

        # ارسال به n8n
        import aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(N8N_WEBHOOK_URL, json={
                    "amount": amount,
                    "title": title,
                    "account": account
                })
            except:
                pass

        context.user_data.clear()
        return

    # وقتی دکمه ریز خرج‌کرد زده می‌شود
    if text == "💰 ریز خرج‌کرد روزانه":
        context.user_data["state"] = "WAIT_EXPENSE"
        await update.message.reply_text(
            "مبلغ + ریال + عنوان + حساب را بفرست\nمثال: ۲۰۰۰۰ ریال اسنپ ملت مهدی",
            reply_markup=ReplyKeyboardRemove(),
        )
        return


# ------------------------------
#     وب‌سرور Railway (لازمه)
# ------------------------------
async def handle_webhook(request):
    application = request.app["application"]
    data = await request.json()
    await application.update_queue.put(data)
    return web.Response(text="OK")


# ------------------------------
#        MAIN APP
# ------------------------------
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # ایجاد وب سرور aiohttp
    app = web.Application()
    app["application"] = application
    app.router.add_post("/webhook", handle_webhook)

    # Start Bot
    await application.initialize()

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    print("Bot is running...")

    await application.start()
    await application.updater.start_polling()


import asyncio
asyncio.run(main())
