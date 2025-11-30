import os
import re
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")

# تبدیل عدد فارسی به انگلیسی
def convert_fa_numbers(text):
    fa = "۰۱۲۳۴۵۶۷۸۹"
    en = "0123456789"
    return text.translate(str.maketrans(fa, en))

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["فروش روزانه", "حقوق"],
        ["برداشت", "موجوی صندوق"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("یک گزینه را انتخاب کنید:", reply_markup=reply_markup)


# هندل پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 ریز خرج‌کرد روزانه":
        context.user_data["state"] = "WAIT_EXPENSE"
        await update.message.reply_text(
            "مبلغ + ریال + عنوان + حساب را بفرست.\nمثال:\n۲۰۰۰۰ ریال اسنپ ملت مهدی",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    if context.user_data.get("state") == "WAIT_EXPENSE":

        raw = convert_fa_numbers(text)

        if "ریال" not in raw:
            await update.message.reply_text("❗ لطفاً مبلغ را همراه «ریال» بفرست.")
            return

        parts = raw.split("ریال")
        amount_text = parts[0].strip()
        after_amount = parts[1].strip()

        nums = re.findall(r"\d+", amount_text)
        if not nums:
            await update.message.reply_text("❗ مبلغ پیدا نشد.")
            return

        amount = int(nums[0])

        words = after_amount.split()
        if len(words) < 2:
            await update.message.reply_text("❗ عنوان و حساب ناقص است.")
            return

        if len(words) >= 3:
            account = " ".join(words[-2:])
            title = " ".join(words[:-2])
        else:
            account = words[-1]
            title = " ".join(words[:-1])

        # ارسال به کاربر
        await update.message.reply_text(
            f"✔ ثبت شد:\n\nمبلغ: {amount}\nعنوان: {title}\nحساب: {account}",
            reply_markup=ReplyKeyboardRemove()
        )

        # ارسال به n8n
        try:
            requests.post(N8N_WEBHOOK_URL, json={
                "amount": amount,
                "title": title,
                "account": account
            })
        except Exception as e:
            print("خطای ارسال به n8n:", e)

        context.user_data.clear()
        return


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # وب‌هوک
    await app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path="telegram",
        webhook_url=N8N_WEBHOOK_URL,
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
