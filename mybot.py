import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

TOKEN = "7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04"
WEBHOOK_URL = "https://bot-production-c6b1.up.railway.app/webhook"   # توجه: اسلش آخر ندارد

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ------------------ دکمه‌ها ------------------
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


# ------------------ start ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("یکی را انتخاب کنید:", reply_markup=keyboard)


# ------------------ message ------------------
async def forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"پیام دریافت شد: {update.message.text}")


# ------------------ main ------------------
async def set_hook(app):
    await app.bot.set_webhook(WEBHOOK_URL)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward))

    # ست کردن وب‌هوک
    app.post_init = set_hook

    # اجرا روی Railway
    app.run_webhook(
        listen="0.0.0.0",
        port=8000,
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    )


if __name__ == "__main__":
    main()
