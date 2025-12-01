import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ---------------------------------------------------
#   تنظیمات اصلی
# ---------------------------------------------------

TOKEN = "7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04"

# آدرس Webhook صحیح Railway (بدون اسلش اضافه)
BOT_WEBHOOK = "https://bot-production-c6bl.up.railway.app/webhook"

# آدرس Webhook نود n8n
N8N_WEBHOOK = "https://n8n-production-4e00.up.railway.app/webhook/telegram"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------
#   دکمه‌های اصلی ربات
# ---------------------------------------------------
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


# ---------------------------------------------------
#   ارسال همه پیام‌ها به n8n
# ---------------------------------------------------
async def forward_to_n8n(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = {
            "user_id": update.message.from_user.id,
            "username": update.message.from_user.username,
            "text": update.message.text
        }

        requests.post(N8N_WEBHOOK, json=data)

    except Exception as e:
        logger.error(f"خطا در ارسال به n8n: {e}")


# ---------------------------------------------------
#   تنظیم وبهوک تلگرام
# ---------------------------------------------------
async def set_webhook(app):
    await app.bot.set_webhook(url=BOT_WEBHOOK)
    print("🚀 Webhook Telegram Set!")


# ---------------------------------------------------
#   اجرای ربات روی Railway
# ---------------------------------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # فرمان /start
    app.add_handler(CommandHandler("start", start))

    # همه پیام‌ها → به n8n
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_n8n))

    # ست کردن وبهو
