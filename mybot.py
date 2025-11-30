from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    # وقتی /start میاد، همیشه برگرد به منوی اصلی
    context.user_data.clear()
    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["گزینه ۲", "گزینه ۳"],
        ["گزینه ۴", "گزینه ۵"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
  update.message.reply_text("یکی از گزینه‌های زیر رو انتخاب کن:", reply_markup=reply_markup)

    
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    # -----------------------------
    # ۱) اگر الان تو منوی اصلی هستیم
    # -----------------------------
    # هنوز وارد فرآیند پول نشدیم
    if not context.user_data.get("state"):
        # فقط اگه روی "ریز خرج‌کرد روزانه" بزنه میریم سراغ مبلغ
        if text == "💰 ریز خرج‌کرد روزانه":
            context.user_data["state"] = "WAITING_AMOUNT"
            update.message.reply_text("لطفاً مبلغ رو به صورت عدد بفرست 💸 (مثلاً 120000)")
            return
        else:
            # بقیه گزینه‌ها فعلاً هیچی انجام ندن
            return

    # -----------------------------
    # ۲) مرحله گرفتن مبلغ
    # -----------------------------
    if context.user_data.get("state") == "WAITING_AMOUNT":
        amount_text = text.strip()

        # چک می‌کنیم که شبیه عدد باشه
        if not amount_text.replace(".", "", 1).isdigit():
            update.message.reply_text("❗ لطفاً مبلغ رو فقط به صورت عدد بفرست (مثلاً 120000).")
            return

        # مبلغ رو ذخیره می‌کنیم برای استفاده‌های بعدی (مثل اکسل یا n8n)
        context.user_data["last_amount"] = amount_text

        # حالا میریم مرحله بعد: انتخاب نوع خرج
        context.user_data["state"] = "WAITING_MONEY_CATEGORY"

        # این ۵ تا دکمه مربوط به بخش پول هست (برای اکسل)
        keyboard = [
            ["دسته ۱", "دسته ۲"],
            ["دسته ۳", "دسته ۴"],
            ["دسته ۵"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        update.message.reply_text(
            f"مبلغ {amount_text} ثبت شد ✔️\nحالا نوع خرج رو انتخاب کن:",
            reply_markup=reply_markup
        )
        return

    # -----------------------------
    # ۳) مرحله انتخاب یکی از ۵ دکمه‌ی پولی
    # -----------------------------
    if context.user_data.get("state") == "WAITING_MONEY_CATEGORY":
        amount = context.user_data.get("last_amount")
        category = text

        # اینجا بعداً می‌تونی این مبلغ و دسته رو بفرستی n8n / اکسل
        # فعلاً فقط تأیید می‌کنیم
        update.message.reply_text(f"✅ خرج {amount} در دسته «{category}» ثبت شد.")

        # بعد از ثبت، دوباره برگرد به منوی اصلی ۵تایی
        context.user_data.clear()

        keyboard = [
            ["💰 ریز خرج‌کرد روزانه"],
            ["گزینه ۲", "گزینه ۳"],
            ["گزینه ۴", "گزینه ۵"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("برگشتیم به منوی اصلی. یکی از گزینه‌ها رو انتخاب کن:", reply_markup=reply_markup)
        return
        

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()




