from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
import re
import requests

def convert_fa_numbers(text):
    fa = "۰۱۲۳۴۵۶۷۸۹"
    en = "0123456789"
    return text.translate(str.maketrans(fa, en))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["فروش روزانه", "حقوق"],
        ["برداشت", "موجوی صندوق"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("یک گزینه را انتخاب کنید:", reply_markup=markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.user_data.get("state") == "WAIT_EXPENSE":

        raw = convert_fa_numbers(text)

        if "ریال" not in raw:
            await update.message.reply_text("❗ لطفاً مبلغ را همراه کلمه «ریال» بفرست.")
            return

        parts = raw.split("ریال")
        amount_text = parts[0].strip()
        after = parts[1].strip()

        nums = re.findall(r"\d+", amount_text)
        if not nums:
            await update.message.reply_text("❗ مبلغ نامعتبر است.")
            return

        amount = int(nums[0])

        words = after.split()
        if len(words) < 2:
            await update.message.reply_text("❗ لطفاً عنوان و حساب را هم ارسال کنید.")
            return

        if len(words) >= 3:
            account = " ".join(words[-2:])
            title = " ".join(words[:-2])
        else:
            account = words[-1]
            title = " ".join(words[:-1])

        # پیام ثبت
        await update.message.reply_text(
            f"✔ ثبت شد\n\nمبلغ: {amount}\nعنوان: {title}\nحساب: {account}",
            reply_markup=ReplyKeyboardRemove()
        )

        # ارسال به n8n
        webhook = os.environ.get("N8N_WEBHOOK_URL")
        try:
            requests.post(webhook, json={
                "amount": amount,
                "title": title,
                "account": account
            })
        except Exception as e:
            print("ERR sending to n8n:", e)

        context.user_data.clear()
        return

    if text == "💰 ریز خرج‌کرد روزانه":
        context.user_data["state"] = "WAIT_EXPENSE"
        await update.message.reply_text(
            "مبلغ + ریال + عنوان + حساب را بفرست.\nمثال: «۲۰۰۰۰ ریال اسنپ ملت مهدی»",
            reply_markup=ReplyKeyboardRemove()
        )
        return

async def main():
    token = os.environ.get("BOT_TOKEN")
    webhook_url = os.environ.get("WEBHOOK_URL")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path="webhook",
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
