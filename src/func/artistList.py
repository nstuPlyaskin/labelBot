# SHOW ARTIST LIST WITH UID + HIS ARTISTS IN DB


from telebot import TeleBot, types
from telebot.types import Message
from func.dbAction import DB
import os

# Путь к базе данных
db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'support')

# artistList.py



# Функция для начала процедуры создания нового артиста
def setup_artistList_handler(bot, message):
    db = DB(db_path)  # Создаем объект класса DB
    showArtists(bot, message, db)

# Функция для вывода списка артистов
def showArtists(bot, message, db):
    uid = message.from_user.id  # Получаем UID пользователя
    artist_list = db.artistList(uid)  # Получаем список артистов по UID пользователя

    # Формируем сообщение с списком артистов
    if artist_list:
        artists_str = "\n".join(artist_list)
        reply_message = f"Список ваших артистов:\n{artists_str}"
    else:
        reply_message = "У вас пока нет артистов в базе данных."

    # Отправляем сообщение с списком артистов в чат
    bot.send_message(message.chat.id, reply_message, reply_markup=types.ReplyKeyboardRemove())

