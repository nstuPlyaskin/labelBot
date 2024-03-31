from telebot import types
from telebot import TeleBot
from ..db.dbAction import DB
import os
from func.shared.keyboard import get_main_keyboard

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')

def setup_releaseList_handler(bot: TeleBot, message):
    db = DB(db_path)
    showRelease(bot, message, db)

def showRelease(bot, message, db):
    try:
        uid = message.from_user.id
        
        # Получаем список артистов для данного UID
        artist_list = db.artistList(uid)

        if artist_list:
            has_releases = False  # Флаг для проверки наличия релизов у всех артистов
            reply_message = ""
            for artist_name in artist_list:
                releases_info = db.showReleaseByArtist(bot, uid, artist_name)
                if releases_info:
                    has_releases = True  # Устанавливаем флаг, если есть хотя бы один релиз
                    reply_message += f"Релизы артиста {artist_name}:\n"
                    for release in releases_info:
                        release_str = f"Название: {release[0]}\nДата выпуска: {release[1]}\n"
                        reply_message += release_str
                else:
                    reply_message += f"У артиста {artist_name} пока нет релизов в базе данных.\n"
            
            # Отправляем сообщение, если хотя бы для одного артиста есть релизы
            if has_releases:
                keyboard = get_main_keyboard()
                bot.send_message(message.chat.id, reply_message, reply_markup=keyboard)
        else:
            keyboard = get_main_keyboard()
            reply_message = "У вас пока нет артистов в базе данных."
            bot.send_message(message.chat.id, reply_message, reply_markup=keyboard)
    except Exception as e:
        keyboard = get_main_keyboard()
        print("Ошибка при получении информации о релизах:", e)
        reply_message = "Произошла ошибка при получении информации о релизах."
        bot.send_message(message.chat.id, reply_message, reply_markup=keyboard)

