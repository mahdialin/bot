import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import pandas as pd
from datetime import datetime
from io import BytesIO  # برای ارسال فایل از حافظه

# تنظیمات اولیه
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن ربات تلگرام
TOKEN = '7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04'

# دیکشنری برای ذخیره داده‌ها
data = {}

# چک کردن اینکه فایل اکسل وجود داره یا نه
def check_excel():
    # فقط یکبار اکسل رو چک میکنیم که اگر نیست، یه فایل جدید بسازیم
    try:
        df = pd.read_excel('expenses.xlsx')
    except FileNotFoundError:
        df = pd.DataFrame(columns=["تاریخ", "عنوان", "مبلغ (ریال)", "حساب"])
        df.to_excel('expenses.xlsx', index=False)

# ساخت فایل اکسل در حافظه و ارسال به کاربر
def send_excel(update: Update, context: CallbackContext):
    df = pd.DataFrame(data)
    # ذخیره فایل در حافظه به جای دیسک
    with BytesIO() as excel_file:
        df.to_excel(excel_file, index=False, engine='openpyxl')
        excel_file.seek(0)  # تنظیم موقعیت فایل برای ارسال
        # ارسال فایل به کاربر
        update.message.reply_document(document=excel_file, filename="expenses.xlsx")
        
# شروع ربات
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "سلام! خوش آمدید. لطفاً دستور خود را وارد کنید.",
        reply_markup=ReplyKeyboardMarkup([['ریز خرج کرد روزانه', 'پایان روز کاری']], one_time_keyboard=True)
    )

# دریافت ویس یا متن
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text.lower()

    if 'ریز خرج کرد روزانه' in user_message:
        update.message.reply_text("لطفاً شرح خرج را وارد کنید (متن یا ویس).")
    else:
        update.message.reply_text("مقدار ورودی شناخته نشد. لطفاً دستور صحیح را وارد کنید.")

# ذخیره و پردازش ویس
def handle_voice(update: Update, context: CallbackContext):
    file = update.message.voice.get_file()
    file.download('voice_note.ogg')
    update.message.reply_text("ویس دریافت شد. در حال پردازش ...")

    # اینجا باید کد تبدیل ویس به متن اضافه بشه
    # فرض می‌کنیم که داده‌های پردازش شده به شکل زیر هستند:
    processed_data = "35000 ریال خرید نان ملت"
    
    process_expense(processed_data)

# پردازش هزینه و ذخیره در اکسل
def process_expense(data_str: str):
    # فرض بر اینکه داده‌ها به این شکل هستند: مبلغ شرح حساب
    try:
        amount, description, account = data_str.split(" ")
        amount = int(amount.replace("ریال", "").strip())
    except ValueError:
        return "فرمت داده‌ها اشتباه است. لطفاً دوباره وارد کنید."

    # ثبت داده در دیکشنری
    date_today = datetime.today().strftime('%Y/%m/%d')
    if 'تاریخ' not in data:
        data['تاریخ'] = []
    if 'عنوان' not in data:
        data['عنوان'] = []
    if 'مبلغ (ریال)' not in data:
        data['مبلغ (ریال)'] = []
    if 'حساب' not in data:
        data['حساب'] = []

    data['تاریخ'].append(date_today)
    data['عنوان'].append(description)
    data['مبلغ (ریال)'].append(amount)
    data['حساب'].append(account)

    # ارسال فایل اکسل بعد از ثبت
    send_excel(update, context)

    # ارسال پیام تایید
    return f"ثبت شد!\nعنوان: {description}\nمبلغ: {amount} ریال\nحساب: {account}\nتاریخ: {date_today}"

# دستور پایان روز
def end_day(update: Update, context: CallbackContext):
    # جمع‌زدن داده‌ها از اکسل
    df = pd.DataFrame(data)
    total = df['مبلغ (ریال)'].sum()

    # ثبت جمع کل در اکسل
    df = df.append({
        'تاریخ': 'پایان روز',
        'عنوان': 'جمع کل',
        'مبلغ (ریال)': total,
        'حساب': 'تمام حساب‌ها'
    }, ignore_index=True)

    send_excel(update, context)

    update.message.reply_text(f"پایان روز کاری! جمع کل خرج‌ها: {total} ریال.")

# اجرای ربات
def main():
    check_excel()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(MessageHandler(Filters.voice, handle_voice))
    dp.add_handler(CommandHandler("end_day", end_day))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
