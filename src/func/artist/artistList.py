from telebot import types
from telebot import TeleBot
from ..db.dbAction import DB
import os
from func.shared.keyboard import get_main_keyboard

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')

def setup_artistList_handler(bot: TeleBot, message):
    db = DB(db_path)
    showArtists(bot, message, db)

def showArtists(bot, message, db):
    uid = message.from_user.id
    artist_list = db.artistList(uid)

    if artist_list:
        artists_str = "\n".join(artist_list)
        reply_message = f"Список ваших артистов:\n{artists_str}"
    else:
        reply_message = "У вас пока нет артистов в базе данных."

    keyboard = get_main_keyboard()  # Получаем клавиатуру с основными кнопками
    bot.send_message(message.chat.id, reply_message, reply_markup=keyboard)
