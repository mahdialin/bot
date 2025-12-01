import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import pandas as pd
from datetime import datetime
from io import BytesIO

# تنظیمات اولیه
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن ربات تلگرام
TOKEN = 'YOUR_BOT_TOKEN'

# دیکشنری برای ذخیره داده‌ها
data = {
    "تاریخ": [],
    "عنوان": [],
    "مبلغ (ریال)": [],
    "حساب": []
}

# ذخیره داده‌ها در اکسل
def save_to_excel():
    df = pd.DataFrame(data)
    with BytesIO() as excel_file:
        df.to_excel(excel_file, index=False, engine='openpyxl')
        excel_file.seek(0)
        return excel_file

# شروع ربات و نمایش دکمه‌ها
def start(update: Update, context: CallbackContext):
    keyboard = [
        ['ریز خرج کرد روزانه'],
        ['فروش روزانه'],
        ['حساب باز'],
        ['دکمه ۴'],
        ['دکمه ۵']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "سلام! انتخاب کنید:",
        reply_markup=reply_markup
    )

# دریافت اطلاعات شرح و مبلغ
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text.lower()

    if 'ریز خرج کرد روزانه' in user_message:
        update.message.reply_text("لطفاً شرح خرج و مبلغ را ارسال کنید (فرمت: مبلغ شرح خرج).")
    else:
        update.message.reply_text("لطفاً یکی از دکمه‌ها را انتخاب کنید.")

# پردازش و ذخیره اطلاعات در دیکشنری
def handle_expense(update: Update, context: CallbackContext):
    user_message = update.message.text
    try:
        # فرض بر این است که ورودی به شکل زیر است: "35000 ریال خرید نان"
        amount, description = user_message.split(" ", 1)
        amount = int(amount.replace("ریال", "").strip())

        # ذخیره در دیکشنری
        date_today = datetime.today().strftime('%Y/%m/%d')
        data["تاریخ"].append(date_today)
        data["عنوان"].append(description)
        data["مبلغ (ریال)"].append(amount)
        data["حساب"].append("ملت")  # می‌توانید حساب را به صورت داینامیک از کاربر بگیرید

        # نمایش دکمه برای انتخاب عنوان خرج
        keyboard = [['اسنپ'], ['حقوق'], ['خرید نان'], ['خرید ماشین'], ['سایر']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text("عنوان خرج را انتخاب کنید:", reply_markup=reply_markup)

    except ValueError:
        update.message.reply_text("فرمت داده‌ها اشتباه است. لطفاً دوباره وارد کنید.")

# ذخیره عنوان انتخابی و ارسال فایل اکسل
def handle_title(update: Update, context: CallbackContext):
    title = update.message.text
    data["عنوان"][-1] = title  # عنوان انتخاب شده به آخرین ردیف اضافه می‌شود

    # ارسال فایل اکسل به کاربر
    excel_file = save_to_excel()
    update.message.reply_document(document=excel_file, filename="expenses.xlsx")

    # ارسال پیام تایید
    update.message.reply_text(f"ثبت شد! عنوان: {title}.")

    # نمایش مجدد دکمه‌ها
    keyboard = [
        ['ریز خرج کرد روزانه'],
        ['فروش روزانه'],
        ['حساب باز'],
        ['دکمه ۴'],
        ['دکمه ۵']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text("انتخاب کنید:", reply_markup=reply_markup)

# اجرای ربات
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(MessageHandler(Filters.text, handle_expense))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_title))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
