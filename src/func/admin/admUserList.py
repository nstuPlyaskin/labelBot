from telebot import TeleBot
from ..db.dbAction import DB
import os
from .isWhitelist import is_user_allowed

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')
whitelist_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'whitelist.json')

def setup_admUserList_handler(bot: TeleBot, message):
    if is_user_allowed(message.from_user.id):
        db = DB(db_path)  # Создаем экземпляр класса DB с путем к базе данных
        db.showUsers(bot, message)  # Вызываем метод showUsers с объектом бота
        db.close()  # Закрываем соединение с базой данных после использования
    else:
        bot.reply_to(message, "Извините, у вас нет доступа к этой команде.")
