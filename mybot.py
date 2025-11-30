from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
import re

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # از Railway میاره

def start(update: Update, context: CallbackContext):
    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["فروش روزانه", "حقوق"],
        ["برداشت", "موجوی صندوق"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("یک گزینه را انتخاب کنید:", reply_markup=reply_markup)

def convert_fa_numbers(text):
    fa = "۰۱۲۳۴۵۶۷۸۹"
    en = "0123456789"
    table = str.maketrans(fa, en)
    return text.translate(table)

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    # اگر وارد حالت ریز خرج‌کرد شدیم
    if context.user_data.get("state") == "WAIT_EXPENSE":

        raw = convert_fa_numbers(text)

        # 1) مبلغ تا قبل از کلمه "ریال"
        if "ریال" not in raw:
            update.message.reply_text("❗ لطفاً مبلغ را همراه کلمه «ریال» بفرست.")
            return

        parts = raw.split("ریال")
        amount_text = parts[0].strip()
        after_amount = parts[1].strip()

        # مبلغ را از پیام جدا کنیم (فقط عدد)
        amount_numbers = re.findall(r"\d+", amount_text)
        if not amount_numbers:
            update.message.reply_text("❗ مبلغ درست تشخیص داده نشد.")
            return

        amount = int(amount_numbers[0])

        # 2) حساب و عنوان
        words = after_amount.split()

        if len(words) < 2:
            update.message.reply_text("❗ لطفاً بعد از مبلغ، عنوان و حساب را هم بفرست.")
            return

        if len(words) >= 3:
            account = " ".join(words[-2:])
            title = " ".join(words[:-2])
        else:
            account = words[-1]
            title = " ".join(words[:-1])

        # پیام به کاربر
        update.message.reply_text(
            f"✔ ثبت شد\n\n"
            f"مبلغ: {amount}\n"
            f"عنوان: {title}\n"
            f"حساب: {account}",
            reply_markup=ReplyKeyboardRemove()
        )

        # ------------------------------
        # ارسال داده‌ها به n8n (Webhook)
        # ------------------------------
        import requests
        webhook_url = os.environ.get("N8N_WEBHOOK_URL")

        try:
            requests.post(webhook_url, json={
                "amount": amount,
                "title": title,
                "account": account
            })
        except Exception as e:
            print("❗ خطا در ارسال به n8n:", e)

        # پاک کردن state
        context.user_data.clear()
        return

    # وقتی روی دکمه ریز خرج‌کرد کلیک میشه
    if text == "💰 ریز خرج‌کرد روزانه":
        context.user_data["state"] = "WAIT_EXPENSE"
        update.message.reply_text(
            "لطفاً مبلغ + ریال + عنوان + حساب را بفرست یا ویس بده.\n"
            "مثال: «۲۰۰۰۰ ریال اسنپ ملت مهدی»",
            reply_markup=ReplyKeyboardRemove()
        )
        return

def main():
    updater = Updater(BOT_TOKEN, use_context=True)

    # ست کردن وبهوک روی Railway
    updater.start_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
    )

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.idle()

if __name__ == "__main__":
    main()

