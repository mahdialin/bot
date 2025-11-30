from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes

# توکن ربات
TOKEN = '7773555006:AAEFzzZ8ZzDyJ02ZnQw2y3Ya4b5jEJGZs04'  # جایگزین کنید با توکن واقعی ربات

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # دکمه‌های اصلی
    keyboard = [
        [InlineKeyboardButton("💰 ریز خرج‌کرد روزانه", callback_data="expense")],
        [InlineKeyboardButton("۲", callback_data="2")],
        [InlineKeyboardButton("۳", callback_data="3")],
        [InlineKeyboardButton("۴", callback_data="4")],
        [InlineKeyboardButton("۵", callback_data="5")]
    ]
    
    # ارسال دکمه‌ها
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! 👋\nلطفاً یک گزینه را انتخاب کنید:",
        reply_markup=reply_markup
    )

# تابع برای مدیریت وضعیت وقتی کاربر "💰 ریز خرج‌کرد روزانه" رو انتخاب می‌کنه
async def expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # حذف دکمه‌های قبلی و نمایش پیام برای ارسال مبلغ
    keyboard = []
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "لطفاً مبلغ را همراه با کلمه «ریال» بفرستید (مثال: ۲۰۰۰۰ ریال).",
        reply_markup=reply_markup
    )
    
    # تغییر حالت به انتظار دریافت مبلغ
    context.user_data['state'] = 'WAIT_EXPENSE'

# تابع برای دریافت مبلغ و ارسال دکمه‌های جدید
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.user_data.get('state') == 'WAIT_EXPENSE':
        # حذف ریال و دریافت مقدار عددی
        amount_text = text.replace("ریال", "").strip()
        try:
            amount = int(amount_text)
        except ValueError:
            await update.message.reply_text("❗ مبلغ صحیح وارد نشده. لطفاً دوباره امتحان کنید.")
            return
        
        # بعد از دریافت مبلغ، نمایش دکمه‌های جدید
        keyboard = [
            [InlineKeyboardButton("خوراک", callback_data="expense_food")],
            [InlineKeyboardButton("رفت‌وآمد", callback_data="expense_transport")],
            [InlineKeyboardButton("خانه", callback_data="expense_home")],
            [InlineKeyboardButton("تفریح", callback_data="expense_fun")],
            [InlineKeyboardButton("سایر", callback_data="expense_other")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"مبلغ ثبت‌شده: {amount} ریال. لطفاً نوع خرج را انتخاب کنید:",
            reply_markup=reply_markup
        )
        # تغییر حالت به انتظار انتخاب نوع خرج
        context.user_data['state'] = 'WAIT_CATEGORY'

# تابع برای پردازش انتخاب نوع خرج
async def process_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    category = query.data  # داده مربوط به دکمه کلیک شده

    # ارسال تایید ثبت خرج
    await query.answer()  # این خط برای پاسخ به کلیک روی دکمه ضروری است
    await query.edit_message_text(
        f"ثبت {category} به عنوان خرج انجام شد. همه چیز تمام است."
    )

    # پاک کردن دکمه‌ها
    keyboard = []
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_reply_markup(reply_markup=reply_markup)

    # تغییر حالت به حالت اولیه
    context.user_data['state'] = 'START'

# تابع اصلی
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # ثبت handlerها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(expense, pattern="^expense$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(process_expense, pattern="^(expense_food|expense_transport|expense_home|expense_fun|expense_other)$"))

    app.run_polling()

if __name__ == "__main__":
    main()
