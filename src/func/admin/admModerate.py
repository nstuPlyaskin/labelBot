from telebot import TeleBot
from ..db.dbAction import DB
import os
from .isWhitelist import is_user_allowed

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')

def moderate_releases(bot: TeleBot, message):
    if is_user_allowed(message.from_user.id):
        if len(message.text.split()) > 1:  # Проверяем, есть ли достаточно аргументов в сообщении
            db = DB(db_path)  # Создаем экземпляр класса DB с путем к базе данных
            release_id = message.text.split()[1]  # Получаем ID релиза из сообщения пользователя
            release_details = db.get_release_details(release_id)  # Получаем детали релиза по его ID
            db.close()  # Закрываем соединение с базой данных после использования

            if release_details:
                release_message = "Детали релиза:\n\n"
                for key, value in release_details.items():
                    release_message += f"{key}: {value}\n"
                bot.send_message(message.chat.id, release_message)
            else:
                bot.send_message(message.chat.id, "Релиз с указанным ID не найден.")
        else:
            bot.reply_to(message, "Пожалуйста, укажите ID релиза после команды.")
    else:
        bot.reply_to(message, "Извините, у вас нет доступа к этой команде.")
