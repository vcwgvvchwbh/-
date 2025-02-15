from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
import random

# توکن ربات
TOKEN = '7811811670:AAED9SHrowkQWy0SkwJRhy0KyrDaQlGwlxU'

# شناسه کانال‌ها
CHANNELS = ["@Advertising_1000", "@bot_mahdi_1000"]

# لیست کاربران در حال چت و صف انتظار
active_chats = {}
waiting_users = []

# دکمه‌ها
def start_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("💬 شروع چت")],
        [KeyboardButton("ℹ️ درباره ما"), KeyboardButton("📜 قوانین")]
    ], resize_keyboard=True)

def stop_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("❌ قطع چت")]
    ], resize_keyboard=True)

def join_channels_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📣 عضویت در کانال 1", url="https://t.me/Advertising_1000")],
        [InlineKeyboardButton("📣 عضویت در کانال 2", url="https://t.me/bot_mahdi_1000")],
        [InlineKeyboardButton("🔄 بررسی عضویت", callback_data="check_membership")]
    ])

# بررسی عضویت کاربر در کانال‌ها
async def is_user_member(user_id: int, context: CallbackContext) -> bool:
    try:
        for channel in CHANNELS:
            chat_member = await context.bot.get_chat_member(channel, user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                return False
        return True
    except Exception:
        return False

# پیام عضویت اجباری
async def send_join_message(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "❗️ **برای استفاده از ربات، ابتدا باید در هر دو کانال ما عضو شوید:**\n"
        "👉 [عضویت در کانال 1](https://t.me/Advertising_1000)\n"
        "👉 [عضویت در کانال 2](https://t.me/bot_mahdi_1000)\n\n"
        "✅ پس از عضویت، دکمه '🔄 بررسی عضویت' را بزنید.",
        reply_markup=join_channels_keyboard(),
        parse_mode="Markdown", 
        disable_web_page_preview=True
    )

# دکمه "درباره ما"
async def about(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🤖 **ربات چت ناشناس**\n\n"
        "👤 **توسعه‌دهنده:** [@mahdi_0_0_0](https://t.me/mahdi_0_0_0)\n"
        "📢 **کانال رسمی:** [@bot_mahdi_1000](https://t.me/bot_mahdi_1000)",
        parse_mode="Markdown"
    )

# دکمه "قوانین"
async def rules(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📜 **قوانین استفاده از ربات:**\n\n"
        "1️⃣ **احترام** به دیگر کاربران الزامی است.\n"
        "2️⃣ ارسال **پیام‌های توهین‌آمیز** یا **تبلیغاتی** ممنوع است.\n"
        "3️⃣ از به اشتراک گذاشتن **اطلاعات شخصی** خودداری کنید.\n"
        "4️⃣ ارسال **محتوای غیرقانونی** باعث **مسدود شدن دائمی** خواهد شد.\n"
        "5️⃣ اینجا برای **چت ناشناس و سالم** ساخته شده، لطفاً قوانین را رعایت کنید. 🙏"
    )

# شروع چت
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if not await is_user_member(user_id, context):
        await send_join_message(update, context)
        return

    await update.message.reply_text(
        "👋 **سلام! خوش آمدید به ربات چت ناشناس!**\n\n"
        "برای شروع چت، دکمه **'💬 شروع چت'** را بزنید.",
        reply_markup=start_keyboard()
    )

# شروع چت در صف
async def start_chat(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # اگر کاربر قبلاً در صف انتظار یا چت فعال بود، به او پیغام داده و از صف خارج کن
    if user_id in active_chats:
        await update.message.reply_text("شما در حال حاضر در یک چت فعال هستید.")
        return

    if user_id not in waiting_users:
        waiting_users.append(user_id)
        await update.message.reply_text("شما به صف انتظار برای چت اضافه شدید. لطفاً منتظر بمانید.")
    else:
        await update.message.reply_text("شما هم‌اکنون در صف انتظار هستید.")

    # اگر دو کاربر در صف انتظار هستند، آنها را به هم وصل کن
    if len(waiting_users) >= 2:
        user1 = waiting_users.pop(0)  # اولین کاربر از صف خارج می‌شود
        user2 = waiting_users.pop(0)  # دومین کاربر از صف خارج می‌شود

        # اتصال کاربران به هم
        active_chats[user1] = user2
        active_chats[user2] = user1

        # ارسال پیام برای دو کاربر
        await context.bot.send_message(user1, "شما با یک کاربر دیگر به صورت ناشناس متصل شدید.\nبرای قطع چت، دکمه '❌ قطع چت' را بزنید.", reply_markup=stop_keyboard())
        await context.bot.send_message(user2, "شما با یک کاربر دیگر به صورت ناشناس متصل شدید.\nبرای قطع چت، دکمه '❌ قطع چت' را بزنید.", reply_markup=stop_keyboard())

        # ارسال پیام به کاربران
        await update.message.reply_text("شما با یک کاربر دیگر به صورت ناشناس متصل شدید. حالا می‌توانید چت کنید.")

# قطع چت
async def stop_chat(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id in active_chats:
        # دریافت کاربر دوم که با کاربر اول چت می‌کند
        partner_id = active_chats[user_id]
        
        # حذف چت‌های فعال
        del active_chats[user_id]
        del active_chats[partner_id]

        await update.message.reply_text("چت شما با موفقیت متوقف شد.", reply_markup=start_keyboard())
        await context.bot.send_message(partner_id, "چت شما با کاربر دیگر متوقف شد.", reply_markup=start_keyboard())
    else:
        await update.message.reply_text("شما هیچ چتی در حال حاضر ندارید.", reply_markup=start_keyboard())

# ارسال پیام‌ها بین دو کاربر متصل
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id in active_chats:
        partner_id = active_chats[user_id]
        message_text = update.message.text
        await context.bot.send_message(partner_id, message_text)

# راه‌اندازی ربات
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex('^ℹ️ درباره ما$'), about))
    application.add_handler(MessageHandler(filters.Regex('^📜 قوانین$'), rules))
    application.add_handler(MessageHandler(filters.Regex('^💬 شروع چت$'), start_chat))
    application.add_handler(MessageHandler(filters.Regex('^❌ قطع چت$'), stop_chat))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
