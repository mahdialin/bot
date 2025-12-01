import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

TOKEN = "7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04"
WEBHOOK_URL = "https://bot-production-c6b1.up.railway.app/webhook"   # ❗️ همین خط مهم است

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💸 ریز خرج کرد روزانه"],
        ["۲"],
        ["۳"],
        ["۴"],
        ["۵"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("یکی را انتخاب کن:", reply_markup=reply_markup)


async def forward_to_n8n(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = {
        "user_id": update.message.from_user.id,
        "username": update.message.from_user.username,
        "text": update.message.text
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        logger.error(e)


async def set_hook(app):
    await app.bot.set_webhook(WEBHOOK_URL)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_n8n))

    app.post_init = set_hook

    app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    )


if __name__ == "__main__":
    main()
