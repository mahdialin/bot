import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)
from fastapi import FastAPI
from telegram import Update
from telegram.request import HTTPXRequest

# --------------------- تنظیمات ---------------------
TOKEN = "7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04"
WEBHOOK_URL = "https://bot-production-c6b1.up.railway.app/webhook"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --------------------- دکمه‌ها ---------------------
main_keyboard = ReplyKeyboardMarkup(
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
    await update.message.reply_text("یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=main_keyboard)

async def forward_to_n8n(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    await update.message.reply_text(f"پیام دریافت شد:\n{msg}")

# --------------------- FastAPI برای وب‌هوک ---------------------
app = FastAPI()

@app.post("/webhook")
async def webhook(update_dict: dict):
    update = Update.de_json(update_dict, application.bot)
    await application.process_update(update)
    return {"ok": True}

# --------------------- اجرای برنامه ---------------------
async def main():
    global application

    req = HTTPXRequest(connection_pool_size=8)
    application = ApplicationBuilder().token(TOKEN).request(req).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_n8n))

    # ست وب‌هوک
    await application.bot.set_webhook(url=WEBHOOK_URL)

    # اجرای FastAPI
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
