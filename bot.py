from aiogram import Bot, Dispatcher, types
from aiogram.types import *
from aiogram.utils import executor
import requests
from bs4 import BeautifulSoup as BS
from pymongo import MongoClient



TOKEN = "5722665625:AAHWYbU2Qeb_frepI4YRmyNVgNC3wUq0kWk"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

myclient = MongoClient("mongodb+srv://admin:user12345@botdb.vssvoe7.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["wallpapers-bot"]
src = mydb["sources"]
peoples = mydb["users"]

# ---------------------------variables-----------------------
lan1 = InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data='uz')
lan2 = InlineKeyboardButton(text="🇷🇺 Русский", callback_data='ru')
lan3 = InlineKeyboardButton(text="🇺🇸 English", callback_data='us')
lans = InlineKeyboardMarkup().row(lan1, lan2, lan3)
control = ReplyKeyboardMarkup(resize_keyboard=True).row("Yana ➡️").row("Asosiy menyu⬆️")
lan = ''
theme = ReplyKeyboardMarkup(resize_keyboard=True)
theme_admin = ReplyKeyboardMarkup(resize_keyboard=True)
cancel = ReplyKeyboardMarkup(resize_keyboard=True).row("Bekor qilish")
ad = False
delete = False
user_name = ''
themes = []
themes_link = []
page = 0
admin = False
caption =''
cap = ''



def add_them():
    global theme, theme_admin, themes, themes_link
    themes = []
    themes_link = []
    royxat = src.find() 
    for i in royxat:
        themes.append(i['name'])
        themes_link.append(i['link'])
    theme = ReplyKeyboardMarkup(resize_keyboard=True)
    theme_admin = ReplyKeyboardMarkup(resize_keyboard=True)

    if len(themes)%2 == 0:
        for i in range(0, len(themes), 2):
            theme.add(themes[i], themes[i+1])
            theme_admin.add(themes[i], themes[i+1])
    else:
        for i in range(0, len(themes)-1, 2):
            theme.add(themes[i], themes[i+1])
            theme_admin.add(themes[i], themes[i+1])
        theme.add(themes[len(themes)-1])
        theme_admin.add(themes[len(themes)-1])
    theme_admin.add('➕ Mavzu qo`shish', '✖️ Mavzuni o`chirish')
    if lan == 'uz':
        theme.add('📊 Statistika')
    elif lan == 'ru':
        theme.add('📊 Статистика')
    elif lan == 'us':
        theme.add('📊 Statistics')
    theme_admin.add('📊 Statistika')

def get_image(link):
    r = requests.get(link)
    soup = BS(r.content, 'html.parser')

    src = soup.find_all('img')
    imgs = []
    for i in src:
        if i.attrs.get('data-src') != None:
            imgs.append(str(i.attrs.get('data-src')))
    return imgs

def check_user():
    users = []
    
    listt = peoples.find()
    for i in listt:
        users.append(i["id"])
    return users

    



# ----------------------------main codes----------------------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    global user_name, admin, users
    users = check_user()

    if not(message.from_user.id in users):
        data = {'id': message.from_user.id}
        peoples.insert_one(data)
    
    add_them()
    user_name = message.from_user.first_name

    if message.from_user.username == "Feruzbek_Sapayev":
        admin = True
        await message.answer("Salom Feruzbek!", reply_markup=theme_admin)
    else:
        await message.answer("*Tilni tanlang | Выберите язык | Select a language*", reply_markup=lans, parse_mode='Markdown')


@dp.message_handler()
async def add_theme(message: types.Message):
    global ad, page, caption, cap, delete
    
    if message.text == "➕ Mavzu qo`shish" and admin:
        ad = True
        await message.answer("Iltimos, mavzu nomini va linkini bir qatorda kiritng masalan: theme link", reply_markup=cancel)

    else:
        if ad and message.text != "Bekor qilish":
            theme_name, theme_url = message.text.split()
            if (theme_name != '') and ("https://www.wallpaperflare.com" in theme_url):
                t = {"name": theme_name, "link": theme_url}
                src.insert_one(t)
                ad= False
                add_them()
                await message.answer('Mavzu muvaffaqiyatli qo`shildi!', reply_markup=theme_admin)
            else:
                await message.answer("Ma`lumotlarni xato kiritdingiz, iltimos tekshirib qayta kiritng!")
    if message.text in themes:
        global images

        if delete:
            n = message.text
            t = {'name': n}
            src.delete_one(t)
            add_them()
            await message.answer("Mavzu muvaffaqiyatli o`chirildi!", reply_markup=theme_admin)

        else:

            cap = f"<b>{message.text}</b>"
            if lan == 'uz':
                caption =cap + "\n\nEng zo'r fon rasmlari shu yerda👇\nhttps://t.me/Fon_Rasmlar_Wallpapers_oboi_bot"
            elif lan == 'ru':
                caption =cap +  "\n\nЛучшие обои здесь👇\nhttps://t.me/Fon_Rasmlar_Wallpapers_oboi_bot"
            elif lan == 'us':
                caption =cap + "\n\nThe best wallpapers are here👇\nhttps://t.me/Fon_Rasmlar_Wallpapers_oboi_bot"
            else:
                caption =cap + "\n\nEng zo'r fon rasmlari shu yerda👇\nhttps://t.me/Fon_Rasmlar_Wallpapers_oboi_bot"
            page = 5
            index = themes.index(message.text)
            images = get_image(themes_link[index])
            i = 0
            while len(images)>i and i<page:
                await bot.send_photo(chat_id=message.chat.id, photo=images[i], caption=caption, reply_markup=control, parse_mode="html")
                i+=1

    if (message.text == "Yana ➡️") or (message.text == "Ещё ➡️") or (message.text == "Next ➡️"):
        
        i = page
        page += 5
        while len(images)>i and page>i:
            await bot.send_photo(chat_id=message.chat.id, photo=images[i], caption=caption, reply_markup=control, parse_mode="html")
            i+=1

    if message.text == "Asosiy menyu⬆️" or message.text == "Главное меню⬆️" or message.text == "Main menu⬆️":
        if message.from_user.username == "Feruzbek_Sapayev":
            await message.answer(message.text, reply_markup=theme_admin)
        else:
            await message.answer(message.text, reply_markup=theme)

    if message.text == '📊 Statistika' or message.text == '📊 Статистика' or message.text == '📊 Statistics':
        if lan == 'uz':
            await message.answer(f"*👨🏻‍💻 Obunachilar soni - {len(check_user())} ta.*\n\n📊 *Fon Rasmlar Bot* statistikasi", parse_mode="Markdown")
        elif lan == 'ru':
            await message.answer(f"*👨🏻‍💻 Количество подписчиков - {len(check_user())} .*\n\n📊 Статистика *ОБОИ БОТА*", parse_mode="Markdown")
        elif lan == 'us':
            await message.answer(f"*👨🏻‍💻 Number of subscribers - {len(check_user())} .*\n\n📊 *WALLPAPERS BOT* statistics", parse_mode="Markdown")
        else:
            await message.answer(f"*👨🏻‍💻 Obunachilar soni - {len(check_user())} ta.*\n\n📊 *Fon Rasmlar Bot* statistikasi", parse_mode="Markdown")
    if message.text == "Bekor qilish":
        ad = False
        delete =False
        await message.answer("Bekor qilindi!", reply_markup=theme_admin)
    if message.text == "✖️ Mavzuni o`chirish" and admin:
        theme_del = theme
        theme_del.add("Bekor qilish")
        await message.answer("Mavzuni tanlang:", reply_markup=theme_del)
        delete = True
        
    


@dp.callback_query_handler(text=['uz', 'ru', 'us'])
async def calls(call: types.CallbackQuery):
    global lan, control
    if call.data == 'uz':
        lan = 'uz'
        add_them()
        await bot.send_message(call.message.chat.id, f" 👋 Assalomu aleykum  *{user_name}*. *FON RASMLARI BOT* ga xush kelibsiz!. \nMarhamat, mavzulardan birini tanlang👇", parse_mode='Markdown', reply_markup=theme)
        control = ReplyKeyboardMarkup(resize_keyboard=True).row("Yana ➡️").row("Asosiy menyu⬆️")
    elif call.data == 'ru':
        lan = 'ru'
        add_them()
        control = ReplyKeyboardMarkup(resize_keyboard=True).row("Ещё ➡️").row("Главное меню⬆️")
        await bot.send_message(call.message.chat.id, f" 👋 Здравствуйте  *{user_name}*. Добро пожаловать в *ОБОИ БОТ!*. \nПожалуйста, выберите одну из тем👇", parse_mode='Markdown', reply_markup=theme)
    elif call.data == 'us':
        lan = 'us'
        add_them()
        control = ReplyKeyboardMarkup(resize_keyboard=True).row("Next ➡️").row("Main menu⬆️")
        await bot.send_message(call.message.chat.id, f" 👋 Hello  *{user_name}*. Welcome to *WALLPAPERS BOT*. \nPlease, choose one of the topics👇", parse_mode='Markdown', reply_markup=theme)


    await call.answer()

if __name__=='__main__':
    executor.start_polling(dp, skip_updates=True)

    
