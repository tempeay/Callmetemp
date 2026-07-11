from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import csv
import asyncio


TOKEN = "8703978282:AAGPYF_UTX4igF5bQm-kHlPw0LIQwQNh1cI"

DB_FILE = "database.csv"


user_state = {}


# -------------------------
# خواندن دیتابیس
# -------------------------

def load_database():

    data = []

    with open(DB_FILE, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:
            data.append(row)

    return data



# -------------------------
# منوی اصلی
# -------------------------

def main_menu():

    keyboard = [
        ["👤 نام و نام خانوادگی"],
        ["📱 شماره تلفن"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )



# -------------------------
# منوی نتیجه
# -------------------------

def result_menu():

    keyboard = [
        [
            "🔙 بازگشت",
            "❌ بستن پنل"
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )



# -------------------------
# استارت
# -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 پنل جستجو\n\nیک گزینه را انتخاب کنید:",
        reply_markup=main_menu()
    )



# -------------------------
# انتخاب نام
# -------------------------

async def select_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_state[update.effective_chat.id] = "name"

    await update.message.reply_text(
        "👤 نام و نام خانوادگی را وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )



# -------------------------
# انتخاب شماره
# -------------------------

async def select_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_state[update.effective_chat.id] = "phone"

    await update.message.reply_text(
        "📱 شماره تلفن را وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )



# -------------------------
# بازگشت
# -------------------------

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_state.pop(update.effective_chat.id, None)

    await update.message.reply_text(
        "🤖 پنل جستجو",
        reply_markup=main_menu()
    )



# -------------------------
# بستن
# -------------------------

async def close(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_state.pop(update.effective_chat.id, None)

    await update.message.reply_text(
        "✅ پنل بسته شد.",
        reply_markup=ReplyKeyboardRemove()
    )



# -------------------------
# جستجو
# -------------------------

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id


    if chat_id not in user_state:

        await update.message.reply_text(
            "ابتدا /start را بزنید."
        )

        return



    text = update.message.text.strip()

    mode = user_state[chat_id]


    msg = await update.message.reply_text(
        "🔍 شروع جستجو..."
    )


    animation = [
        "🔍 بررسی اطلاعات...",
        "📂 باز کردن دیتابیس...",
        "🛰 جستجو...",
        "✅ پایان جستجو..."
    ]


    for a in animation:

        await asyncio.sleep(0.5)

        await msg.edit_text(a)



    database = load_database()


    found = None


    for person in database:


        if mode == "name":

            if person["name"] == text:
                found = person
                break


        if mode == "phone":

            if person["phone"] == text:
                found = person
                break



    if found:


        keyboard = None


        if found.get("telegram_id"):


            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📩 ورود به پیوی تلگرام",
                            url=f"tg://openmessage?user_id={found['telegram_id']}"
                        )
                    ]
                ]
            )



        await msg.edit_text(
            "✅ اطلاعات پیدا شد"
        )


        await update.message.reply_text(

f"""
╔══════════════╗
   ✅ نتیجه
╚══════════════╝

👤 نام:
{found['name']}

📱 شماره:
{found['phone']}

🆔 آیدی تلگرام:
{found.get('telegram_id','ندارد')}
""",

            reply_markup=keyboard
        )


    else:


        await msg.edit_text(
            "❌ چیزی پیدا نشد"
        )


    user_state.pop(chat_id, None)



# -------------------------
# اجرای ربات
# -------------------------

app = Application.builder().token(TOKEN).build()


app.add_handler(
    CommandHandler("start", start)
)


app.add_handler(
    MessageHandler(filters.Regex("^👤 نام و نام خانوادگی$"), select_name)
)


app.add_handler(
    MessageHandler(filters.Regex("^📱 شماره تلفن$"), select_phone)
)


app.add_handler(
    MessageHandler(filters.Regex("^🔙 بازگشت$"), back)
)


app.add_handler(
    MessageHandler(filters.Regex("^❌ بستن پنل$"), close)
)


app.add_handler(
    MessageHandler(filters.TEXT, search)
)


print("Bot is running...")

app.run_polling()