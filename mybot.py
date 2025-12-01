import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TOKEN = "7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04"

# چون Railway ریشه '/' را اجرا می‌کند، پس فقط دامنه را می‌دهیم
WEBHOOK_URL = "https://bot-production-c6bl.up.railway.app"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# -----------------------  /start  -----------------------
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


# -------------------- Forward to N8N --------------------
async def forward_to_n8n(update: Update, context: ContextTypes.DEFAULT_TYPE):

    payload = {
        "user_id": update.message.from_user.id,
        "username": update.message.from_user.username,
        "text": update.message.text,
    }

    # ارسال پیام به n8n
    try:
        requests.post("https://n8n-production-4e00.up.railway.app/webhook/telegram", json=payload)
    except Exception as e:
        logger.error(f"N8N ERROR: {e}")


# ------------------------- MAIN -------------------------
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    # هندلر ها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_n8n))

    # 🚀 ست کردن وبهوک فقط یک بار
    app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path="",              # ربات روی مسیر "/" اجرا می‌شود
        webhook_url=WEBHOOK_URL   # اینو به تلگرام اعلام می‌کنیم
    )


if __name__ == "__main__":
    main()
