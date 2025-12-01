import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

TOKEN = "7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04"
WEBHOOK_URL = "https://bot-production-c6bl.up.railway.app/webhook"


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ---------------------
#  /start
# ---------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💸 ریز خرج کرد روزانه"],
        ["۲"],
        ["۳"],
        ["۴"],
        ["۵"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "لطفاً یک گزینه را انتخاب کنید:",
        reply_markup=reply_markup
    )


# ---------------------
#  Forward to N8N
# ---------------------
async def forward_to_n8n(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payload = {
        "user_id": update.message.from_user.id,
        "username": update.message.from_user.username,
        "text": update.message.text,
    }

    try:
        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        logger.error(f"N8N ERROR: {e}")


# ---------------------
#  Set Telegram Webhook
# ---------------------
async def set_webhook(app):
    await app.bot.set_webhook(WEBHOOK_URL)


# ---------------------
#  Main
# ---------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_n8n))

    app.post_init = set_webhook

    app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    )


if __name__ == "__main__":
    main()
