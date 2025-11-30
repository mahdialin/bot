from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    keyboard = [
        ["💰 ریز خرج‌کرد روزانه"],
        ["گزینه ۲", "گزینه ۳"],
        ["گزینه ۴", "گزینه ۵"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text("یک گزینه را انتخاب کنید:", reply_markup=reply_markup)

    
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    # اگر کاربر گزینه "ریز خرج‌کرد روزانه" را انتخاب کرد
    if text == "💰 ریز خرج‌کرد روزانه":
        context.user_data["step"] = "waiting_amount"
        update.message.reply_text("سلام 👋\nلطفاً مبلغت رو بفرست (فعلاً فقط عدد).")
        return

    # اگر منتظر مبلغ هستیم
    if context.user_data.get("step") == "waiting_amount":
        update.message.reply_text(f"مبلغ {text} ثبت شد ✔️")

        # بعد از ثبت مبلغ، کیبورد ۵ گزینه دوباره نمایش داده می‌شه
        keyboard = [
            ["💰 ریز خرج‌کرد روزانه"],
            ["گزینه ۲", "گزینه ۳"],
            ["گزینه ۴", "گزینه ۵"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        update.message.reply_text("یک گزینه را انتخاب کنید:", reply_markup=reply_markup)

        context.user_data["step"] = None
        return

    # اگر گزینه اشتباه زد
    update.message.reply_text("لطفاً یکی از گزینه‌ها را انتخاب کنید 👇")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()





