from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
import re
import requests

# ---------------------------
#  ENV VARIABLES
# ---------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")   # این باید دقیقا URL وب‌هوک n8n باشد
# مثال:
# https://n8n-production-4e00.up.railway.app/webhook/telegram

# ---------------------------
#  START COMMAND
# ---------------------------

def start(update: Update, context: CallbackContext):
    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["فروش روزانه", "حقوق"],
        ["برداشت", "موجوی صندوق"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("یک گزینه را انتخاب کنید:", reply_markup=reply_markup)

# ---------------------------
#  فارسی → انگلیسی عدد
# ---------------------------

def convert_fa_numbers(text):
    fa = "۰۱۲۳۴۵۶۷۸۹"
    en = "0123456789"
    return text.translate(str.maketrans(fa, en))

# ---------------------------
#  MESSAGE HANDLER
# ---------------------------

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    # کاربر روی دکمه ریز خرج کرد زده
    if text == "💰 ریز خرج‌کرد روزانه":
        context.user_data["state"] = "WAIT_EXPENSE"
        update.message.reply_text(
            "لطفاً مبلغ + ریال + عنوان + حساب را بفرست.\nمثال: ۲۰۰۰۰ ریال اسنپ ملت مهدی",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # اگر در حالت انتظار هزینه هستیم
    if context.user_data.get("state") == "WAIT_EXPENSE":

        raw = convert_fa_numbers(text)

        if "ریال" not in raw:
            update.message.reply_text("❗ لطفاً مبلغ را همراه «ریال» بفرست.")
            return

        parts = raw.split("ریال")
        amount_text = parts[0].strip()
        after_amount = parts[1].strip()

        # استخراج مبلغ
        nums = re.findall(r"\d+", amount_text)
        if not nums:
            update.message.reply_text("❗ مبلغ پیدا نشد.")
            return
        amount = int(nums[0])

        # عنوان + حساب
        words = after_amount.split()

        if len(words) < 2:
            update.message.reply_text("❗ لطفاً عنوان و حساب را کامل بفرست.")
            return

        if len(words) >= 3:
            account = " ".join(words[-2:])
            title = " ".join(words[:-2])
        else:
            account = words[-1]
            title = " ".join(words[:-1])

        # پاسخ به کاربر
        update.message.reply_text(
            f"✔ ثبت شد:\n\n"
            f"مبلغ: {amount}\n"
            f"عنوان: {title}\n"
            f"حساب: {account}",
            reply_markup=ReplyKeyboardRemove()
        )

        # ارسال داده به n8n
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


# ---------------------------
#  WEBHOOK MODE
# ---------------------------

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # webhook باید با مسیر n8n یکی باشد
    updater.start_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path="telegram",   # این باید EXACT با webbook n8n یکی باشد
        webhook_url=N8N_WEBHOOK_URL
    )

    updater.idle()

if __name__ == "__main__":
    main()
