from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import os
import requests
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
N8N_URL = os.getenv("N8N_WEBHOOK_URL")


def convert_fa_numbers(text):
    fa = "۰۱۲۳۴۵۶۷۸۹"
    en = "0123456789"
    return text.translate(str.maketrans(fa, en))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["فروش روزانه", "حقوق"],
        ["برداشت", "موجوی صندوق"]
    ]
    await update.message.reply_text(
        "یک گزینه را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.user_data.get("state") == "WAIT_EXPENSE":
        raw = convert_fa_numbers(text)

        if "ریال" not in raw:
            await update.message.reply_text("❗ لطفاً مبلغ + کلمه «ریال» را بفرست.")
            return

        parts = raw.split("ریال")
        amount_text = parts[0].strip()
        after = parts[1].strip()

        nums = re.findall(r"\d+", amount_text)
        if not nums:
            await update.message.reply_text("❗ مبلغ تشخیص داده نشد.")
            return

        amount = int(nums[0])
        words = after.split()

        if len(words) < 2:
            await update.message.reply_text("❗ باید عنوان + حساب را بفرستی.")
            return

        if len(words) >= 3:
            account = " ".join(words[-2:])
            title = " ".join(words[:-2])
        else:
            account = words[-1]
            title = " ".join(words[:-1])

        await update.message.reply_text(
            f"✔ ثبت شد\n\n"
            f"مبلغ: {amount}\n"
            f"عنوان: {title}\n"
            f"حساب: {account}",
            reply_markup=ReplyKeyboardRemove()
        )

        try:
            requests.post(N8N_URL, json={
                "amount": amount,
                "title": title,
                "account": account
            })
        except:
            pass

        context.user_data.clear()
        return

    if text == "💰 ریز خرج‌کرد روزانه":
        context.user_data["state"] = "WAIT_EXPENSE"
        await update.message.reply_text(
            "فرمت: مبلغ + ریال + عنوان + حساب",
            reply_markup=ReplyKeyboardRemove()
        )


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # handler ها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # فقط همین!  
    # Railway خودش مدیریت می‌کنه — run_webhook حذف شد
    await app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
