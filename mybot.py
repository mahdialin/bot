import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import os

TOKEN = os.getenv("bot7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["👌 شروع"]]
    await update.message.reply_text("سلام! ربات فعاله.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# پیام‌های معمولی
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("پیامت رسید 👍")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # ست کردن وب‌هوک
    await app.start()
    await app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

