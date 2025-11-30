import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
import logging

# Logging
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

# ---------------------- Handlers ----------------------

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("ارسال پیام", callback_data="send_message")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("سلام! یکی از گزینه‌ها را انتخاب کن:", reply_markup=reply_markup)

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "send_message":
        await query.message.reply_text("پیام خود را ارسال کنید:")
        context.user_data["expecting_message"] = True

async def receive_message(update: Update, context: CallbackContext):
    if context.user_data.get("expecting_message"):
        text = update.message.text
        context.user_data["expecting_message"] = False

        # ارسال به n8n
        import requests
        try:
            requests.post(N8N_WEBHOOK_URL, json={"message": text})
        except Exception as e:
            print("Error sending to n8n:", e)

        await update.message.reply_text("پیام شما ارسال شد!")

# ---------------------- Main ----------------------      

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message))

    # ---- IMPORTANT ----
    # نسخه درست شده بدون webhook_url
    await app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path="telegram"
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
