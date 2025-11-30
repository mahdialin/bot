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
    state = context.user_data.get("state")

    # =========================
    # مرحله ۱: منوی اصلی
    # =========================
    if state is None:
        # فقط اگر "ریز خرج‌کرد روزانه" را زد
        if text == "💰 ریز خرج‌کرد روزانه":
            # میریم به حالت گرفتن مبلغ
            context.user_data["state"] = "WAIT_AMOUNT"

            # دکمه‌های منوی اصلی را می‌بندیم
            update.message.reply_text(
                "لطفاً مبلغ رو به صورت عدد بفرست 💸 (مثلاً 120000)",
                reply_markup=ReplyKeyboardRemove()
            )
        # اگر یکی از دکمه‌های ۲،۳،۴،۵ یا چیز دیگه زد، فعلاً کاری نکن
        return

    # =========================
    # مرحله ۲: گرفتن مبلغ
    # =========================
    if state == "WAIT_AMOUNT":
        amount = text.strip()

        # چک ساده که شبیه عدد باشه
        if not amount.replace(".", "", 1).isdigit():
            update.message.reply_text("❗ لطفاً مبلغ رو فقط به صورت عدد بفرست (مثلاً 120000).")
            return

        # مبلغ رو ذخیره می‌کنیم
        context.user_data["last_amount"] = amount
        context.user_data["state"] = "WAIT_CATEGORY"

        # اینجا کیبوردِ جدید (۵ دکمه‌ی خرج) میاد
        keyboard = [
            ["🍔 خوراک", "🚕 رفت‌وآمد"],
            ["🏠 خانه", "🎉 تفریح"],
            ["💼 سایر"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        update.message.reply_text(
            f"مبلغ {amount} ثبت شد ✔️\nحالا نوع خرج رو انتخاب کن:",
            reply_markup=reply_markup
        )
        return

    # =========================
    # مرحله ۳: انتخاب دسته‌ی خرج
    # =========================
    if state == "WAIT_CATEGORY":
        amount = context.user_data.get("last_amount")
        category = text  # همون دکمه‌ای که زد

        # اینجا بعداً می‌فرستیمش n8n/اکسل، فعلاً فقط تأیید می‌کنیم
        update.message.reply_text(
            f"✅ خرج {amount} در دسته «{category}» ثبت شد.",
            reply_markup=ReplyKeyboardRemove()  # دکمه‌ها هم می‌رن
        )

        # همه‌چیز ریست می‌شه؛ برای شروع دوباره باید /start بزنه
        context.user_data.clear()
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







