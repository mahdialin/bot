from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["فروش روزانه", "حقوق"],
        ["برداشت", "موجوی صندوق"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text("یک گزینه را انتخاب کنید:", reply_markup=reply_markup)

    
import re

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
        amount_text = parts[0].strip()          # قبل از ریال
        after_amount = parts[1].strip()         # بعد از ریال (عنوان + حساب)

        # مبلغ را از پیام جدا کنیم (فقط عدد)
        amount_numbers = re.findall(r"\d+", amount_text)
        if not amount_numbers:
            update.message.reply_text("❗ مبلغ درست تشخیص داده نشد.")
            return

        amount = int(amount_numbers[0])

        # 2) حساب = آخرین یک تا دو کلمه
        words = after_amount.split()

        if len(words) < 2:
            update.message.reply_text("❗ لطفاً بعد از مبلغ، عنوان و حساب را هم بفرست.")
            return

        # حساب = آخرین 1 یا 2 یا 3 کلمه (انعطاف‌پذیر)
        if len(words) >= 3:
            # تشخیص هوشمند 2 کلمه آخری حساب
            account = " ".join(words[-2:])
            title = " ".join(words[:-2])
        else:
            account = words[-1]
            title = " ".join(words[:-1])

        # پاسخ نهایی
        update.message.reply_text(
            f"✔ ثبت شد\n\n"
            f"مبلغ: {amount}\n"
            f"عنوان: {title}\n"
            f"حساب: {account}",
            reply_markup=ReplyKeyboardRemove()
        )

        # پاک کردن state برای شروع جدید
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
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    PORT = int(os.environ.get("PORT", 8443))
    WEBHOOK_URL = "https://n8n-production-1119.up.railway.app/webhook/88c3c5d3-4ed9-4b27-bfa2-7cac001be867"

    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="",
        webhook_url=WEBHOOK_URL
    )

    updater.idle()

if __name__ == "__main__":
    main()











