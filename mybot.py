import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # باید = https://bot-production-c6b1.up.railway.app/webhook باشد

# -----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("دریافت اطلاعات", callback_data="get_info")]
    ]
    await update.message.reply_text(
        "سلام! 👋\nروی دکمه زیر بزن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# -----------------------------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = {"user_id": query.from_user.id, "action": query.data}
    requests.post(WEBHOOK_URL, json=data)

    await query.edit_message_text("درخواست ارسال شد ✔")

# -----------------------------

async def webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return

# -----------------------------

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_webhook(
        listen="0.0.0.0",
        port=8000,
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
