from telebot import TeleBot
from ..db.dbAction import DB
import os
from .isWhitelist import is_user_allowed  # Изменен импорт

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')

def show_unmoderated_releases(bot: TeleBot, message):
    if is_user_allowed(message.from_user.id):
        db = DB(db_path)
        unmoderated_releases = db.get_unmoderated_releases()  # Метод должен вернуть список словарей
        
        if unmoderated_releases:
            release_message = "Немодерированные релизы:\n\n"
            for release in unmoderated_releases:
                artist_name = db.get_artist_name_by_id(release['artistID'])  # Получаем имя артиста по его ID
                release_message += f"ID: {release['releaseID']}, Название: {release['releaseName']}, Исполнитель: {artist_name}\n"
            bot.send_message(message.chat.id, release_message)
        else:
            bot.send_message(message.chat.id, "Немодерированные релизы отсутствуют.")
        
        db.close()  # Закрываем базу данных после использования
    else:
        bot.reply_to(message, "Извините, у вас нет доступа к этой команде.")
