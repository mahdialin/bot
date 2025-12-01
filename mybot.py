import os
import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# ---------- تنظیمات ----------
TOKEN = "7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04"

WEBHOOK_PATH = "webhook"
WEBHOOK_BASE = "https://bot-production-c6b1.up.railway.app"   # دامنه Railway
WEBHOOK_URL = f"{WEBHOOK_BASE}/{WEBHOOK_PATH}"

N8N_WEBHOOK = "https://n8n-production-4e00.up.railway.app/webhook/telegram"

PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ---------- کیبوردها ----------
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["💸 ریز خرج کرد روزانه"],
        ["۲"],
        ["۳"],
        ["۴"],
        ["۵"],
    ],
    resize_keyboard=True,
)

CATEGORY_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["1"],
        ["2"],
        ["3"],
        ["4"],
        ["مورد خاص"],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


# ---------- توابع کمکی ----------
def send_to_n8n(payload: dict):
    """ارسال هر مرحله به n8n"""
    try:
        requests.post(N8N_WEBHOOK, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"Error sending to N8N: {e}")


def get_user_info(update: Update):
    u = update.message.from_user
    return {
        "user_id": u.id,
        "username": u.username,
        "first_name": u.first_name,
        "last_name": u.last_name,
    }


# ---------- هندلر /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # پاک کردن وضعیت قبلی کاربر
    context.user_data.clear()

    await update.message.reply_text(
        "سلام 👋\nیکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=MAIN_KEYBOARD,
    )


# ---------- وقتی دکمه یا متن می‌آید ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    state = context.user_data.get("state")

    # برای راحتی
    info = get_user_info(update)

    # ---- مرحله ۱: کلیک روی "ریز خرج کرد روزانه" ----
    if text == "💸 ریز خرج کرد روزانه" and state is None:
        context.user_data["state"] = "await_expense_text"

        await update.message.reply_text(
            "مبلغ + شرح + حساب را در *یک پیام* ارسال کنید.\n"
            "مثال:\n"
            "`250000 ریال ناهار ملت`\n\n"
            "اگر در چند پیام جدا بفرستید، ثبت نمی‌شود.",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown",
        )
        return

    # ---- مرحله ۲: دریافت فرمت «مبلغ ریال شرح حساب» ----
    if state == "await_expense_text":
        if "ریال" not in text:
            await update.message.reply_text(
                "فرمت اشتباه است ❌\n"
                "لطفاً دقیقاً مثل مثال بفرست:\n"
                "`250000 ریال ناهار ملت`",
                parse_mode="Markdown",
            )
            return

        # اینجا فعلاً پارس دقیق را می‌سپاریم به n8n
        payload = {
            "step": "expense_raw",
            "flow": "daily_expense",
            "text": text,
            **info,
        }
        send_to_n8n(payload)

        # رفتن به مرحله انتخاب دسته‌بندی
        context.user_data["state"] = "await_category"

        await update.message.reply_text(
            "لطفاً عنوان/دسته‌ی این خرج را انتخاب کن:",
            reply_markup=CATEGORY_KEYBOARD,
        )
        return

    # ---- مرحله ۳: انتخاب دسته‌بندی 1 تا 4 یا "مورد خاص" ----
    if state == "await_category":
        if text in ["1", "2", "3", "4"]:
            payload = {
                "step": "expense_category",
                "flow": "daily_expense",
                "category": text,       # 1 یا 2 یا 3 یا 4
                "is_custom": False,
                **info,
            }
            send_to_n8n(payload)

            # پایان فرایند
            context.user_data.clear()
            await update.message.reply_text(
                "اطلاعات ثبت شد و تمام ✔",
                reply_markup=MAIN_KEYBOARD,
            )
            return

        if text == "مورد خاص":
            context.user_data["state"] = "await_custom_title"
            await update.message.reply_text(
                "عنوان مورد خاص را بنویس (مثلاً: کپسول آتش‌نشانی):",
            )
            return

        # اگر چیز دیگری فرستاد
        await update.message.reply_text(
            "لطفاً یکی از دکمه‌ها را انتخاب کن.",
            reply_markup=CATEGORY_KEYBOARD,
        )
        return

    # ---- مرحله ۴: دریافت عنوان برای «مورد خاص» ----
    if state == "await_custom_title":
        custom_title = text

        payload = {
            "step": "expense_category",
            "flow": "daily_expense",
            "category": "custom",
            "custom_title": custom_title,
            "is_custom": True,
            **info,
        }
        send_to_n8n(payload)

        context.user_data.clear()
        await update.message.reply_text(
            "اطلاعات ثبت شد و تمام ✔",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    # ---- خارج از فرایند (حالت عادی) ----
    # می‌تونیم اینجا هرچی خواستی بزنی، فعلاً فقط راهنمایی می‌کنیم
    await update.message.reply_text(
        "برای ثبت خرج روی «💸 ریز خرج کرد روزانه» بزن.",
        reply_markup=MAIN_KEYBOARD,
    )


# (اختیاری) هندلر ویس → فقط فوروارد به n8n (برای آینده)
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info = get_user_info(update)
    voice = update.message.voice
    file_id = voice.file_id

    payload = {
        "step": "voice",
        "flow": "daily_expense",
        "file_id": file_id,
        **info,
    }
    send_to_n8n(payload)

    await update.message.reply_text(
        "ویس ارسال شد 🎙\n"
        "فعلاً لطفاً متن را هم به صورت تایپ‌شده بفرست تا ثبت شود.",
    )


# ---------- راه‌اندازی اپ ----------
async def post_init(app):
    # ست کردن وبهوک در تلگرام
    await app.bot.set_webhook(WEBHOOK_URL)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.post_init = post_init

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=WEBHOOK_URL,
    )


if __name__ == "__main__":
    main()
