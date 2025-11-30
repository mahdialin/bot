import os
import re
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))  # پورت Railway

# -----------------------------
# شروع
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["فروش روزانه", "حقوق"],
        ["برداشت", "موجوی صندوق"]
    ]
    await update.message.reply_text(
        "یک گزینه را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# -----------------------------
# تبدیل اعداد فارسی
# -----------------------------
def convert_fa_numbers(text):
    fa = "۰۱۲۳۴۵۶۷۸۹"
    en = "0123456789"
    return text.translate(str.maketrans(fa, en))

# -----------------------------
# هندل پیام
# -----------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.user_data.get("state") == "WAIT_EXPENSE":
        raw = convert_fa_numbers(text)

        if "ریال" not in raw:
            await update.message.reply_text("❗ لطفاً مبلغ را همراه «ریال» بفرست.")
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
            await update.message.reply_text("❗ عنوان و حساب را هم وارد کن.")
            return

        if len(words) >= 3:
            account = " ".join(words[-2:])
            title = " ".join(words[:-2])
        else:
            account = words[-1]
            title = " ".join(words[:-1])

        await update.message.reply_text(
            f"✔ ثبت شد\n\nمبلغ: {amount}\nعنوان: {title}\nحساب: {account}",
            reply_markup=ReplyKeyboardRemove()
        )

        try:
            requests.post(N8N_WEBHOOK_URL, json={
                "amount": amount,
                "title": title,
                "account": account
            })
        except Exception as e:
            print("Error sending to n8n:", e)

        context.user_data.clear()
        return

    if text == "💰 ریز خرج‌کرد روزانه":
        context.user_data["state"] = "WAIT_EXPENSE"
        await update.message.reply_text(
            "مبلغ + ریال + عنوان + حساب را بفرست.\nمثال:\n«۲۰۰۰۰ ریال اسنپ ملت مهدی»",
            reply_markup=ReplyKeyboardRemove()
        )
        return

# -----------------------------
# اصلی
# -----------------------------
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # ---- کاملاً درست ----
    await application.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=N8N_WEBHOOK_URL.split("/")[-1],  # فقط UUID
        webhook_url=N8N_WEBHOOK_URL,
    )

    await application.updater.start_polling()
    await application.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
