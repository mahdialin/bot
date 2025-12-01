import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)
import os

TOKEN = "7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04"
WEBHOOK_BASE = "https://bot-production-c6b1.up.railway.app"   # بدون /webhook
WEBHOOK_URL = f"{WEBHOOK_BASE}/webhook"

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
async def post_init(app):
    await app.bot.set_webhook(WEBHOOK_URL)

def main():
    PORT = int(os.getenv("PORT", "8080"))  # ✔ مطابق Railway

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward))

    app.post_init = post_init  # ✔ فقط یک بار وب‌هوک ست می‌شود

    # ✔ پورت درست  
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
