from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    # مرحله اول → منتظر مبلغ هستیم
    context.user_data["waiting_for_amount"] = True

    update.message.reply_text(
        "سلام 👋\nلطفاً مبلغت رو بفرست (فعلاً فقط عدد).",
        reply_markup=ReplyKeyboardRemove()  # 👈 این خط کیبورد قبلی رو می‌بنده
    )
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    # اگر منتظر مبلغ هستیم
    if context.user_data.get("waiting_for_amount"):
        context.user_data["last_amount"] = text
        context.user_data["waiting_for_amount"] = False

        # نمایش گزینه‌ها
        keyboard = [
            ["گزینه ۱", "گزینه ۲", "گزینه ۳"],
            ["گزینه ۴", "گزینه ۵"],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        update.message.reply_text(
            f"مبلغت ثبت شد: {text}\nحالا یکی از گزینه‌ها رو انتخاب کن 👇",
            reply_markup=reply_markup,
        )
        return

    # اگر مبلغ قبلاً گرفته شده
    if text == "گزینه ۱":
        update.message.reply_text("🍀 شما گزینه ۱ رو انتخاب کردید")
    elif text == "گزینه ۲":
        update.message.reply_text("🔥 شما گزینه ۲ رو انتخاب کردید")
    elif text == "گزینه ۳":
        update.message.reply_text("💎 گزینه ۳ انتخاب شد")
    elif text == "گزینه ۴":
        update.message.reply_text("✨ گزینه ۴ انتخاب شد")
    elif text == "گزینه ۵":
        update.message.reply_text("👌 گزینه ۵ انتخاب شد")
    else:
        update.message.reply_text("اگر می‌خوای دوباره از اول شروع کنی /start رو بزن 🙂")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()


