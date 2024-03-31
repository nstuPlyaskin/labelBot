from telebot import TeleBot
from ..db.dbAction import DB
from ..artist.addArtist import setup_addArtist_handler

from func.shared.keyboard import get_add_artist_keyboard, get_existing_artist_keyboard
import os

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')

def setup_artistInfo_handler(bot: TeleBot, message):
    db = DB(db_path)
    uid = message.from_user.id
    
    if not db.checkUIDExists(uid):
        bot.reply_to(message, "Для просмотра информации по артистам необходимо добавить хотя бы одного артиста в нашу систему.", 
                     reply_markup=get_add_artist_keyboard())
        setup_addArtist_handler(bot, message)  # Начинаем процесс создания нового артиста
    else:
        bot.reply_to(message, "Выберите опцию:", reply_markup=get_existing_artist_keyboard())
    
    db.close()

