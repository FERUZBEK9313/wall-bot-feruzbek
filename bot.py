from aiogram import Bot, Dispatcher, types
from aiogram.types import *
from aiogram.utils import executor
import requests
from bs4 import BeautifulSoup as BS
from pymongo import MongoClient



TOKEN = "5803790907:AAFjOndmwlwpuXnNeaHqf_6LUJUMUsdGhoE"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

myclient = MongoClient("mongodb+srv://admin:user12345@botdb.vssvoe7.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["wallpapers-bot"]
src = mydb["sources"]
peoples = mydb["users"]

# ---------------------------variables-----------------------

control = ReplyKeyboardMarkup(resize_keyboard=True).row("Yana ➡️").row("Asosiy menyu⬆️")
theme = ReplyKeyboardMarkup(resize_keyboard=True)
theme_admin = ReplyKeyboardMarkup(resize_keyboard=True)
theme_delete = ReplyKeyboardMarkup(resize_keyboard=True)
cancel = ReplyKeyboardMarkup(resize_keyboard=True).row("Bekor qilish")
ad = False
delete = False
user_name = ''
themes = []
themes_link = []
page = 0
caption =''
cap = ''



def add_them():
    global theme, theme_admin, themes,theme_delete, themes_link
    
    themes = []
    themes_link = []

    
    royxat = src.find() 
    for i in royxat:
        themes.append(i['name'])
        themes_link.append(i['link'])
    theme = ReplyKeyboardMarkup(resize_keyboard=True)
    theme_admin = ReplyKeyboardMarkup(resize_keyboard=True)
    theme_delete = ReplyKeyboardMarkup(resize_keyboard=True)


    if len(themes)%2 == 0:
        for i in range(0, len(themes), 2):
            theme.add(themes[i], themes[i+1])
            theme_admin.add(themes[i], themes[i+1])
            theme_delete.add(themes[i], themes[i+1])
    else:
        for i in range(0, len(themes)-1, 2):
            theme.add(themes[i], themes[i+1])
            theme_admin.add(themes[i], themes[i+1])
            theme_delete.add(themes[i], themes[i+1])
        theme.add(themes[len(themes)-1])
        theme_delete.add(themes[len(themes)-1])
        theme_admin.add(themes[len(themes)-1])

    theme_admin.add('➕ Mavzu qo`shish', '✖️ Mavzuni o`chirish')
    theme.add('📊 Statistika')
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

def add_user(id):
    users = []
    listt = peoples.find()
    for i in listt:
        users.append(i["id"])
    if not(id in users):
        data = {'id': id}
        peoples.insert_one(data)
    
def check_user(id):
    users = []
    listt = peoples.find()
    for i in listt:
        users.append(i["id"])
    if id in users:
        return True
    else:
        return False
    
def len_users():
    users = 0
    lenn = peoples.find()
    for i in lenn:
        users+=1
    return users


# ----------------------------main codes----------------------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    global user_name, user_id

    user_id = message.from_user.id
    user_name = message.from_user.first_name

    add_them()
    if check_user(user_id):
        if message.from_user.username == "Feruzbek_Sapayev":
            await message.answer("Salom Feruzbek!", reply_markup=theme_admin)
        
        else:
            await bot.send_message(message.chat.id, f" 👋 Assalomu aleykum  *{user_name}*. *FON RASMLARI BOT* ga xush kelibsiz!. \nMarhamat, mavzulardan birini tanlang👇", parse_mode='Markdown', reply_markup=theme)
            

    else:
        if message.from_user.username == "Feruzbek_Sapayev":
            await message.answer("Salom Feruzbek!", reply_markup=theme_admin)

        else:
            await bot.send_message(message.chat.id, f" 👋 Assalomu aleykum  *{user_name}*. *FON RASMLARI BOT* ga xush kelibsiz!. \nMarhamat, mavzulardan birini tanlang👇", parse_mode='Markdown', reply_markup=theme)
        add_user(user_id)
    
#----------------------------------events----------------------------
@dp.message_handler()
async def add_theme(message: types.Message):
    global ad, page, caption, cap, delete



    if message.text == "➕ Mavzu qo`shish" and message.from_user.username == "Feruzbek_Sapayev":
        ad = True
        await message.answer("Iltimos, mavzu nomini va linkini bir qatorda kiritng masalan: theme link", reply_markup=cancel)

    else:
        if ad and message.text != "Bekor qilish":
            theme_name, theme_url = message.text.split()
            if (theme_name != '') and ("https://www.wallpaperflare.com" in theme_url):
                t = {"name": theme_name, "link": theme_url}
                src.insert_one(t)
                ad= False
                add_them(message.from_user.id)
                await message.answer('Mavzu muvaffaqiyatli qo`shildi!', reply_markup=theme_admin)
            else:
                await message.answer("Ma`lumotlarni xato kiritdingiz, iltimos tekshirib qayta kiritng!")
    if message.text in themes:
        global images

        if delete:
            n = message.text
            t = {'name': n}
            src.delete_one(t)
            add_them(message.from_user.id)
            await message.answer("Mavzu muvaffaqiyatli o`chirildi!", reply_markup=theme_admin)

        else:

            cap = f"<b>{message.text}</b>"
            caption =cap + "\n\nEng zo'r fon rasmlari shu yerda👇\n@SFWallpapersBot"
            
            page = 5
            index = themes.index(message.text)
            images = get_image(themes_link[index])
            i = 0
            while len(images)>i and i<page:
                await bot.send_photo(chat_id=message.chat.id, photo=images[i], caption=caption, reply_markup=control, parse_mode="html")
                i+=1

    if (message.text == "Yana ➡️"):
        
        i = page
        page += 5
        while len(images)>i and page>i:
            await bot.send_photo(chat_id=message.chat.id, photo=images[i], caption=caption, reply_markup=control, parse_mode="html")
            i+=1

    if message.text == "Asosiy menyu⬆️":
        if message.from_user.username == "Feruzbek_Sapayev":
            await message.answer(message.text, reply_markup=theme_admin)
        else:
            add_them()
            await message.answer(message.text, reply_markup=theme)

    if message.text == '📊 Statistika':
        t = len_users()
        await message.answer(f"*👨🏻‍💻 Obunachilar soni - {t} ta.*\n\n📊 @SFWallpapersBot statistikasi", parse_mode="Markdown")
    
    if message.text == "Bekor qilish":
        ad = False
        delete =False
        await message.answer("Bekor qilindi!", reply_markup=theme_admin)
    if message.text == "✖️ Mavzuni o`chirish" and message.from_user.username == "Feruzbek_Sapayev":
        theme_del = theme_delete
        theme_del.add("Bekor qilish")
        await message.answer("Mavzuni tanlang:", reply_markup=theme_del)
        delete = True
        
    




if __name__=='__main__':
    executor.start_polling(dp, skip_updates=True)

    
