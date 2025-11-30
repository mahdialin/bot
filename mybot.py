import os
import re
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")

def convert_fa_numbers(text):
    fa = "۰۱۲۳۴۵۶۷۸۹"
    en = "0123456789"
    return text.translate(str.maketrans(fa, en))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["فروش روزانه", "حقوق"],
        ["برداشت", "موجودی صندوق"],
    ]
    await update.message.reply_text(
        "یک گزینه را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 ریز خرج‌کرد روزانه":
        context.user_data["state"] = "WAIT_EXPENSE"
        await update.message.reply_text(
            "مبلغ + ریال + عنوان + حساب را بفرست.\nمثال: ۲۰۰۰۰ ریال اسنپ ملت مهدی",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    if context.user_data.get("state") == "WAIT_EXPENSE":

        raw = convert_fa_numbers(text)

        if "ریال" not in raw:
            await update.message.reply_text("❗ لطفاً مبلغ را همراه «ریال» ارسال کنید.")
            return

        amount_text, after_amount = raw.split("ریال")
        nums = re.findall(r"\d+", amount_text)
        if not nums:
            await update.message.reply_text("❗ مبلغ تشخیص داده نشد.")
            return

        amount = int(nums[0])
        words = after_amount.strip().split()

        if len(words) < 2:
            await update.message.reply_text("❗ عنوان و حساب کامل نیست.")
            return

        if len(words) >= 3:
            account = " ".join(words[-2:])
            title = " ".join(words[:-2])
        else:
            account = words[-1]
            title = " ".join(words[:-1])

        await update.message.reply_text(
            f"✔ ثبت شد:\n\nمبلغ: {amount}\nعنوان: {title}\nحساب: {account}",
            reply_markup=ReplyKeyboardRemove()
        )

        try:
            requests.post(N8N_WEBHOOK_URL, json={
                "amount": amount,
                "title": title,
                "account": account
            })
        except Exception as e:
            print("خطای ارسال به n8n:", e)

        context.user_data.clear()


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path="telegram",
        webhook_url=N8N_WEBHOOK_URL,
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
