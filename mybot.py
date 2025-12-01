import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import pandas as pd
from datetime import datetime
from io import BytesIO

# تنظیمات اولیه
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن ربات تلگرام
TOKEN = '7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04'

# دیکشنری برای ذخیره داده‌ها
data = {
    "تاریخ": [],
    "عنوان": [],
    "مبلغ (ریال)": [],
    "حساب": []
}

def save_to_excel():
    df = pd.DataFrame(data)
    with BytesIO() as excel_file:
        df.to_excel(excel_file, index=False, engine='openpyxl')
        excel_file.seek(0)
        return excel_file

def start(update: Update, context: CallbackContext):
    keyboard = [
        ['ریز خرج کرد روزانه'],
        ['فروش روزانه'],
        ['حساب باز'],
        ['دکمه ۴'],
        ['دکمه ۵']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("سلام! لطفاً یک گزینه را انتخاب کنید:", reply_markup=reply_markup)

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    if text == "ریز خرج کرد روزانه":
        update.message.reply_text("لطفاً شرح خرج را ارسال کنید.\n(فرمت: مبلغ ریال شرح...)")
        context.user_data["waiting_expense"] = True
    else:
        update.message.reply_text("لطفاً یکی از دکمه‌ها را انتخاب کنید.")

def handle_expense(update: Update, context: CallbackContext):
    if not context.user_data.get("waiting_expense"):
        return

    msg = update.message.text

    try:
        amount = msg.split("ریال")[0].strip()
        description = msg.split("ریال")[1].strip()
        amount = int(amount)

        date_today = datetime.today().strftime("%Y/%m/%d")

        data["تاریخ"].append(date_today)
        data["عنوان"].append(description)
        data["مبلغ (ریال)"].append(amount)
        data["حساب"].append("نامشخص")

        keyboard = [['اسنپ'], ['حقوق'], ['خرید'], ['کالا'], ['سایر']]
        update.message.reply_text("عنوان خرج را انتخاب کنید:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

        context.user_data["waiting_expense"] = False
        context.user_data["waiting_title"] = True

    except:
        update.message.reply_text("فرمت ورودی اشتباه است. مثال:\n\n350000 ریال خرید نان")

def handle_title(update: Update, context: CallbackContext):
    if not context.user_data.get("waiting_title"):
        return

    title = update.message.text
    data["عنوان"][-1] = title

    excel = save_to_excel()
    update.message.reply_document(excel, filename="report.xlsx")

    update.message.reply_text("ثبت شد ✔️")

    context.user_data["waiting_title"] = False

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_expense))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
