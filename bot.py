from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import csv
import time


TOKEN = "8703978282:AAF93XBDA7ymHp5aXkuCLWvXHHiiRnuPNWw"

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
# بستن پنل
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

        "🔍 شروع جستجو."

    )



    animation = [

        "🔍 شروع جستجو..",

        "📡 اتصال به سرور..",

        "📂 باز کردن پایگاه داده..",

        "🛰 اسکن اطلاعات..",

        "🔎 بررسی رکوردها.."

    ]


    for item in animation:

        time.sleep(0.2)

        try:

            await msg.edit_text(item)

        except:

            pass



    try:

        database = load_database()

    except:

        await msg.edit_text(

            "❌ خطا در خواندن دیتابیس"

        )

        return



    found = None



    for person in database:


        if mode == "name":

            if person["name"] == text:

                found = person

                break



        elif mode == "phone":

            if person["phone"] == text:

                found = person

                break




    if found:


        await msg.edit_text(

            "✅ جستجو کامل شد\n\n🎯 نتیجه پیدا شد"

        )


        await update.message.reply_text(

f"""
╔══════════════╗
   ✅ اطلاعات پیدا شد
╚══════════════╝

👤 نام:
{found['name']}

📱 شماره:
{found['phone']}
""",

            reply_markup=result_menu()

        )


    else:


        await msg.edit_text(

            "❌ جستجو کامل شد\n\nموردی پیدا نشد."

        )


        await update.message.reply_text(

            "دوباره تلاش کنید:",

            reply_markup=main_menu()

        )



    user_state.pop(chat_id, None)



# -------------------------
# اجرای ربات
# -------------------------

app = Application.builder().token(TOKEN).build()



app.add_handler(
    CommandHandler(
        "start",
        start
    )
)



app.add_handler(
    MessageHandler(
        filters.Regex("^👤 نام و نام خانوادگی$"),
        select_name
    )
)



app.add_handler(
    MessageHandler(
        filters.Regex("^📱 شماره تلفن$"),
        select_phone
    )
)



app.add_handler(
    MessageHandler(
        filters.Regex("^🔙 بازگشت$"),
        back
    )
)



app.add_handler(
    MessageHandler(
        filters.Regex("^❌ بستن پنل$"),
        close
    )
)



app.add_handler(
    MessageHandler(
        filters.TEXT,
        search
    )
)



print("Bot is running...")

app.run_polling()