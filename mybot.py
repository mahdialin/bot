import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import pandas as pd
from datetime import datetime
from io import BytesIO

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# اینجا توکن واقعی رباتت را بگذار
TOKEN = 'توکن_ربات_خودت'

# ساختار داده‌ها برای اکسل
data = {
    "تاریخ": [],
    "عنوان": [],
    "مبلغ (ریال)": [],
    "حساب": []
}

def main_keyboard():
    return ReplyKeyboardMarkup(
        [
            ['ریز خرج کرد روزانه'],
            ['فروش روزانه'],
            ['حساب باز'],
            ['گزینه ۴'],
            ['گزینه ۵'],
        ],
        resize_keyboard=True
    )

def category_keyboard():
    return ReplyKeyboardMarkup(
        [
            ['اسنپ'],
            ['حقوق'],
            ['خرید روزمره'],
            ['کرایه'],
            ['سایر'],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def save_to_excel():
    df = pd.DataFrame(data)
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False, engine='openpyxl')
    excel_file.seek(0)
    return excel_file

def start(update: Update, context: CallbackContext):
    # ریست وضعیت کاربر
    context.user_data.clear()
    update.message.reply_text(
        "سلام 👋\nیک گزینه را انتخاب کنید:",
        reply_markup=main_keyboard()
    )

def handle_text(update: Update, context: CallbackContext):
    text = (update.message.text or "").strip()
    state = context.user_data.get("state")

    # ۱) اگر کاربر تازه دکمه انتخاب می‌کند
    if text == 'ریز خرج کرد روزانه':
        context.user_data["state"] = "waiting_expense"
        update.message.reply_text(
            "شرح خرج را در یک پیام بفرست.\n"
            "فرمت پیشنهادی:\n"
            "`350000 ریال خرید نان ملت`\n"
            "یا حداقل: `350000 ریال خرید نان`",
            parse_mode='Markdown'
        )
        return

    # (فعلاً بقیه دکمه‌ها کاری ندارند)
    if text in ['فروش روزانه', 'حساب باز', 'گزینه
