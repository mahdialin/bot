import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04"
WEBHOOK_PATH = "webhook"
WEBHOOK_URL = f"https://bot-production-c6b1.up.railway.app/{WEBHOOK_PATH}"

PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

keyboard = ReplyKeyboardMarkup(
    [
        ["💸 ریز خرج کرد روزانه"],
        ["📊 گزارش هفتگی"],
        ["🧮 خلاصه ماهانه"],
        ["➕ ثبت هزینه جدید"],
        ["⚙️ تنظیمات"]
    ],
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("یکی از گزینه‌ها را انتخاب کنید:", reply_markup=keyboard)


async def forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"پیام دریافت شد: {update.message.text}")


async def post_init(app):
    await app.bot.set_webhook(WEBHOOK_URL)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward))

    app.post_init = post_init

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=WEBHOOK_URL,
    )


if __name__ == "__main__":
    main()
