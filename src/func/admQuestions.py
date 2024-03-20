from telebot import TeleBot
from func.dbAction import DB
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'support')

def setup_admQuestions_handler(bot: TeleBot, message):
    db = DB(db_path)  # Создаем экземпляр класса DB с путем к базе данных
    db.showQuestions(bot, message)  # Вызываем метод showQuestions с объектом бота
    db.close()  # Закрываем соединение с базой данных после использования
