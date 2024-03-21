from telebot import types
from telebot.types import Message
from telebot import TeleBot
from func.dbAction import DB
import os, json

db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'support')

from telebot import types

def setup_artistInfo_handler(bot: TeleBot, message):
    # Создаем экземпляр класса DB с путем к базе данных
    db = DB(db_path)

    # Проверяем наличие записи в таблице artistTable с UID текущего пользователя Telegram
    uid = message.from_user.id
    if not db.checkArtistExists(uid):
        # Если запись отсутствует, предлагаем пользователю зарегистрировать нового артиста
        bot.reply_to(message, "Для загрузки релиза необходимо добавить в нашу систему никнейм артиста.", 
                     reply_markup=get_add_artist_keyboard())
    else:
        # Если запись существует, предлагаем пользователю просмотреть список артистов и релизов
        bot.reply_to(message, "Что вы хотите сделать?", reply_markup=get_existing_artist_keyboard())

    db.close()  # Закрываем соединение с базой данных после использования

# Функция для получения клавиатуры с кнопками "Добавить артиста"
def get_add_artist_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_add_artist = types.KeyboardButton(text="Добавить артиста")
    keyboard.add(button_add_artist)
    return keyboard

# Функция для получения клавиатуры с кнопками "Список артистов" и "Список релизов"
def get_existing_artist_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_list_artists = types.KeyboardButton(text="Список артистов")
    button_list_releases = types.KeyboardButton(text="Список релизов")
    keyboard.add(button_list_artists, button_list_releases)
    return keyboard