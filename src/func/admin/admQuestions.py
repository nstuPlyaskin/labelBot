from telebot import TeleBot
from ..db.dbAction import DB
import os
from .isWhitelist import is_user_allowed  # Изменен импорт

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')

def setup_admQuestions_handler(bot: TeleBot, message):
    if is_user_allowed(message.from_user.id):
        db = DB(db_path)
        db.showQuestions(bot, message)
        db.close()
    else:
        bot.reply_to(message, "Извините, у вас нет доступа к этой команде.")
