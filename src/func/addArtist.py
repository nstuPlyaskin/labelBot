from telebot import TeleBot, types
from telebot.types import Message
from func.dbAction import DB
import os
from func.artistInfo import get_existing_artist_keyboard

# Путь к базе данных
db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'support')

# Переменные для хранения вопросов и соответствующих им ключей
questions = [
    "Введите никнейм артиста:",
    "Введите настоящее ФИО артиста:",
    "Введите ссылку на профиль артиста в Spotify (если нужно создать новый, напишите 'нужен новый'):",
    "Введите ссылку на официальное сообщество артиста (vk или tg):"
]
keys = ["artistNickName", "artistRealName", "artistSpotify", "artistContacts"]

# Счетчик для отслеживания текущего вопроса
current_question_index = 0

# Словарь для хранения данных пользователя
user_data = {}

# Функция для отправки следующего вопроса и регистрации обработчика ответа
def send_next_question(bot: TeleBot, message: Message):
    global current_question_index, user_data
    
    if current_question_index < len(questions):
        # Проверяем, есть ли uid в объекте сообщения
        if message.from_user.id:
            # Добавляем uid в user_data
            user_data['uid'] = message.from_user.id
        
        bot.send_message(message.chat.id, questions[current_question_index])
        bot.register_next_step_handler(message, save_user_answer, bot=bot)
    else:
        # Все вопросы заданы, отправляем данные в функцию addArtist
        db = DB(db_path)
        success = db.addArtist(user_data)
        db.close()

        if success:
            bot.send_message(message.chat.id, "Артист успешно добавлен.", reply_markup=get_existing_artist_keyboard())
        else:
            bot.send_message(message.chat.id, "Произошла ошибка при добавлении артиста.")


# Функция для сохранения ответа пользователя и перехода к следующему вопросу
from func.dbAction import DB

def save_user_answer(message: Message, bot: TeleBot):
    global current_question_index, user_data
    
    current_key = keys[current_question_index]
    user_answer = message.text.strip()
    
    # Проверяем, существует ли артист с указанным никнеймом
    if current_key == "artistNickName":
        db = DB(db_path)
        if db.check_artist_exists(user_answer):
            bot.send_message(message.chat.id, "Такой артист уже существует. Пожалуйста, введите другой никнейм:")
            # Регистрируем обработчик для следующего ответа пользователя на тот же вопрос
            bot.register_next_step_handler(message, save_user_answer, bot=bot)
            return  # Выходим из функции, чтобы дождаться нового ответа пользователя
    
    user_data[current_key] = user_answer
    current_question_index += 1
    send_next_question(bot, message)


# Основная функция для начала опроса
def setup_addArtist_handler(bot: TeleBot, message: Message):
    global current_question_index, user_data
    current_question_index = 0
    user_data.clear()
    send_next_question(bot, message)
