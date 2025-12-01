import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TOKEN = "7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04"
WEBHOOK_URL = "https://bot-production-c6bl.up.railway.app"     # مهم! بدون /webhook

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

N8N_URL = "https://n8n-production-4e00.up.railway.app/webhook/telegram"


# /start → دکمه‌ها
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💸 ریز خرج کرد روزانه"],
        ["۲"], ["۳"], ["۴"], ["۵"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("لطفاً یک گزینه را انتخاب کنید:", reply_markup=reply_markup)


# هر پیام → به n8n
async def forward_to_n8n(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payload = {
        "user_id": update.message.from_user.id,
        "username": update.message.from_user.username,
        "text": update.message.text
    }
    try:
        requests.post(N8N_URL, json=payload)
    except Exception as e:
        logger.error(f"Error sending to N8N: {e}")


# تنظیم وبهوک
async def set_webhook(app):
    await app.bot.set_webhook(url=WEBHOOK_URL)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_n8n))

    app.post_init = set_webhook

    app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path="webhook",                  # خالی بگذار
        webhook_url=WEBHOOK_URL       # مهم! اشتباه نکن
    )


if __name__ == "__main__":
    main()

