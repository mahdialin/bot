from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
import requests
import re

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# تبدیل اعداد فارسی به انگلیسی
def convert_fa_numbers(text):
    fa = "۰۱۲۳۴۵۶۷۸۹"
    en = "0123456789"
    table = str.maketrans(fa, en)
    return text.translate(table)

# شروع ربات
def start(update: Update, context: CallbackContext):
    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["فروش روزانه", "حقوق"],
        ["برداشت", "موجودی صندوق"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text("یک گزینه را انتخاب کنید:", reply_markup=reply_markup)

# دریافت پیام کاربران
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    # اگر وارد حالت ریز خرج‌کرد شدیم
    if context.user_data.get("state") == "WAIT_EXPENSE":
        raw = convert_fa_numbers(text)

        if "ریال" not in raw:
            update.message.reply_text("❗ لطفاً مبلغ را همراه کلمه «ریال» بفرست.")
            return

        parts = raw.split("ریال")
        amount_text = parts[0].strip()
        after_amount = parts[1].strip()

        amount_numbers = re.findall(r"\d+", amount_text)
        if not amount_numbers:
            update.message.reply_text("❗ مبلغ درست تشخیص داده نشد.")
            return

        amount = int(amount_numbers[0])

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

        # ارسال اطلاعات به n8n Webhook
        webhook_url = os.environ.get("N8N_WEBHOOK_URL")
        if webhook_url:
            requests.post(webhook_url, json={
                "amount": amount,
                "title": title,
                "account": account,
                "user": update.message.from_user.username
            })

        update.message.reply_text(
            f"✔ ثبت شد\n\n"
            f"مبلغ: {amount}\n"
            f"عنوان: {title}\n"
            f"حساب: {account}",
            reply_markup=ReplyKeyboardRemove()
        )

        context.user_data.clear()
        return

    # وقتی روی دکمه ریز خرج‌کرد کلیک می‌شود
    if text == "💰 ریز خرج‌کرد روزانه":
        context.user_data["state"] = "WAIT_EXPENSE"
        update.message.reply_text(
            "لطفاً مبلغ + ریال + عنوان + حساب را بفرست.\n"
            "مثال: «۲۰۰۰۰ ریال اسنپ ملت مهدی»",
            reply_markup=ReplyKeyboardRemove()
        )
        return

# تابع اصلی
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
