import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import re
import requests

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # دقیقا همونی که ست کردی

# تبدیل اعداد فارسی به انگلیسی
def convert_fa_numbers(text):
    fa = "۰۱۲۳۴۵۶۷۸۹"
    en = "0123456789"
    table = str.maketrans(fa, en)
    return text.translate(table)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["فروش روزانه", "حقوق"],
        ["برداشت", "موجودی صندوق"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("یک گزینه را انتخاب کنید:", reply_markup=reply_markup)

# پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # حالت هزینه
    if context.user_data.get("state") == "WAIT_EXPENSE":

        raw = convert_fa_numbers(text)

        if "ریال" not in raw:
            await update.message.reply_text("❗ لطفاً مبلغ را همراه کلمه «ریال» بفرست.")
            return

        parts = raw.split("ریال")
        amount_text = parts[0].strip()
        after_amount = parts[1].strip()

        # استخراج عدد
        amount_numbers = re.findall(r"\d+", amount_text)
        if not amount_numbers:
            await update.message.reply_text("❗ مبلغ درست تشخیص داده نشد.")
            return

        amount = int(amount_numbers[0])

        # حساب و عنوان
        words = after_amount.split()
        if len(words) < 2:
            await update.message.reply_text("❗ لطفاً بعد از مبلغ، عنوان و حساب را هم بفرست.")
            return

        if len(words) >= 3:
            account = " ".join(words[-2:])
            title = " ".join(words[:-2])
        else:
            account = words[-1]
            title = " ".join(words[:-1])

        # پیام تأیید
        await update.message.reply_text(
            f"✔ ثبت شد\n\nمبلغ: {amount}\nعنوان: {title}\nحساب: {account}",
            reply_markup=ReplyKeyboardRemove()
        )

        # ارسال به n8n
        N8N_URL = os.environ.get("N8N_WEBHOOK_URL")
        if N8N_URL:
            try:
                requests.post(N8N_URL, json={
                    "amount": amount,
                    "title": title,
                    "account": account
                })
            except Exception as e:
                print("خطای ارسال به n8n:", e)

        context.user_data.clear()
        return

    # ورود به حالت هزینه
    if text == "💰 ریز خرج‌کرد روزانه":
        context.user_data["state"] = "WAIT_EXPENSE"
        await update.message.reply_text(
            "لطفاً مبلغ + ریال + عنوان + حساب را بفرست\nمثال: «۲۰۰۰۰ ریال اسنپ ملت مهدی»",
            reply_markup=ReplyKeyboardRemove()
        )
        return


# اجرای اصلی
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # برای Railway
    await application.start()
    await application.bot.set_webhook(WEBHOOK_URL)
    await application.updater.start_polling()  # برای مدیریت داخلی
    await application.wait_closed()

import asyncio
asyncio.run(main())
