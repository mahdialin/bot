import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TOKEN = "7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04"
WEBHOOK_URL = "https://n8n-production-4e00.up.railway.app/webhook/telegram"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -----------------------------
#   /start command + buttons
# -----------------------------
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

# -----------------------------
#   Send every message to N8N
# -----------------------------
async def forward_to_n8n(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        payload = {
            "user_id": update.message.from_user.id,
            "username": update.message.from_user.username,
            "text": update.message.text,
        }

        # ارسال داده به N8N
        requests.post(WEBHOOK_URL, json=payload)

    except Exception as e:
        logger.error(f"Error sending to N8N: {e}")

# -----------------------------
#    Main function
# -----------------------------
async def set_webhook(app):
    await app.bot.set_webhook(url=f"{WEBHOOK_URL}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # فرمان start
    app.add_handler(CommandHandler("start", start))

    # هر پیام → ارسال به N8N
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_n8n))

    # تنظیم وبهوک هنگام اجرا
    app.post_init = set_webhook

    # اجرای Webhook server
    app.run_webhook(
        listen="0.0.0.0",
        port=8080,               # Railway از همین استفاده می‌کند
        url_path="",             # خالی بگذار
        webhook_url=WEBHOOK)

