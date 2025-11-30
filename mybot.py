from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# توکن ربات خودتون رو اینجا قرار بدید
TOKEN = "توکن_ربات_شما"

# تابع start که با دکمه‌ها کار می‌کند
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # دکمه‌های اصلی
    keyboard = [
        [InlineKeyboardButton("💰 ریز خرج‌کرد روزانه", callback_data="expense")],
        [InlineKeyboardButton("۲", callback_data="2")],
        [InlineKeyboardButton("۳", callback_data="3")],
        [InlineKeyboardButton("۴", callback_data="4")],
        [InlineKeyboardButton("۵", callback_data="5")]
    ]
    
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
            f"✔ مبلغ {amount} ریال ثبت شد.\nلطفاً نوع خرج را انتخاب کنید:",
            reply_markup=reply_markup
        )

        # پاک کردن حالت
        context.user_data['state'] = None

# مدیریت کلیک روی دکمه‌های خرج
async def handle_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # پاسخ به درخواست

    # مشخص کردن نوع خرج
    expense_type = query.data.split('_')[1]  # مثلاً "food", "transport", "home" و غیره

    # ارسال پیام تأیید
    await query.edit_message_text(text=f"✔ خرج {expense_type} ثبت شد.")

    # پاک کردن دکمه‌ها
    keyboard = []
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_reply_markup(reply_markup=reply_markup)

# ایجاد اپلیکیشن
app = ApplicationBuilder().token(TOKEN).build()

# اضافه کردن هدلرها
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(handle_expense))

# راه‌اندازی ربات
app.run_polling()
