from telebot import TeleBot, types
from telebot.types import Message
from ..db.dbAction import DB
from ..shared.keyboard import get_cancel_keyboard, get_existing_artist_keyboard, get_main_keyboard

import os

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')

# Переменные для хранения вопросов и соответствующих им ключей
questions = [
    "Введите никнейм артиста:",
    "Введите настоящее ФИО артиста:",
    "Введите ссылку на профиль артиста в Spotify (если нужно создать новый, напишите 'нужен новый'):",
    "Введите ссылку на официальное сообщество артиста (vk или tg):"
]

confrimQuestions = [
    "Никнейм артиста:", 
    "Настоящее ФИО артиста:",
    "Ссылка на профиль артиста в Spotify:",
    "Ссылка на официальное сообщество артиста (vk или tg):"
]

keys = ["artistNickName", "artistRealName", "artistSpotify", "artistContacts"]

# Словарь для хранения данных пользователя
user_states = {}

# Функция для отправки следующего вопроса и регистрации обработчика ответа
def send_next_question(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    if user_id not in user_states:
        user_states[user_id] = {'current_question_index': 0, 'user_data': {}, 'questions_summary': []}
        
    current_question_index = user_states[user_id]['current_question_index']
    user_data = user_states[user_id]['user_data']
    questions_summary = user_states[user_id]['questions_summary']
    
    if current_question_index < len(questions):
        keyboard = get_cancel_keyboard() if current_question_index > 0 else None
        
        bot.send_message(message.chat.id, questions[current_question_index], reply_markup=keyboard)
        bot.register_next_step_handler(message, save_user_answer, bot=bot)
    else:
        send_confirmation_message(bot, message)

# Функция для сохранения ответа пользователя и перехода к следующему вопросу
def save_user_answer(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    current_question_index = user_states[user_id]['current_question_index']
    user_data = user_states[user_id]['user_data']
    questions_summary = user_states[user_id]['questions_summary']
    
    # Проверяем, написал ли пользователь "Отмена"
    if message.text.strip().lower() == "отмена":
        bot.send_message(message.chat.id, "Процедура создания артиста отменена.", reply_markup=get_main_keyboard())
        del user_states[user_id]
        return
    
    current_key = keys[current_question_index]
    user_answer = message.text.strip()
    
    if current_key == "artistNickName":
        db = DB(db_path)
        if db.check_artist_exists(user_answer):
            bot.send_message(message.chat.id, "Такой артист уже существует. Пожалуйста, введите другой никнейм:")
            bot.register_next_step_handler(message, save_user_answer, bot=bot)
            return
    
    user_data[current_key] = user_answer
    questions_summary.append(f"{questions[current_question_index]} {user_answer}")
    current_question_index += 1
    user_states[user_id]['current_question_index'] = current_question_index
    user_states[user_id]['user_data'] = user_data
    user_states[user_id]['questions_summary'] = questions_summary
    send_next_question(bot, message)

# Функция для отправки сообщения с подтверждением введенной информации
def send_confirmation_message(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    user_data = user_states[user_id]['user_data']
    questions_summary = user_states[user_id]['questions_summary']

    confirmation_text = ""
    for question, summary in zip(confrimQuestions, questions_summary):
        confirmation_text += f"{question} {summary.split(': ')[1]}\n"  # Используем только ответы пользователя

    final_question = "Вы уверены, что хотите добавить этого артиста?"
    bot.send_message(message.chat.id, f"Пожалуйста, подтвердите введенную информацию:\n\n{confirmation_text}\n{final_question}", 
                     reply_markup=get_confirmation_keyboard())
    bot.register_next_step_handler(message, handle_confirmation_response, bot=bot)

# Функция для обработки ответа пользователя на подтверждение информации
def handle_confirmation_response(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    if message.text.lower() == "да":
        user_data = user_states[user_id]['user_data']
        db = DB(db_path)
        success = db.addArtist(user_data)
        db.close()

        if success:
            bot.send_message(message.chat.id, "Артист успешно добавлен.", reply_markup=get_existing_artist_keyboard())
        else:
            bot.send_message(message.chat.id, "Произошла ошибка при добавлении артиста.")
        del user_states[user_id]
    elif message.text.lower() == "нет":
        # Пользователь хочет изменить информацию, начинаем процесс сначала
        del user_states[user_id]
        setup_addArtist_handler(bot, message)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите 'Да' или 'Нет'.")

# Функция для создания клавиатуры с кнопками "Да" и "Нет" для подтверждения информации
def get_confirmation_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_yes = types.KeyboardButton("Да")
    button_no = types.KeyboardButton("Нет")
    keyboard.add(button_yes, button_no)
    return keyboard

# Функция для начала процедуры создания нового артиста
def setup_addArtist_handler(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    user_states[user_id] = {'current_question_index': 0, 'user_data': {'uid': user_id}, 'questions_summary': []}
    keyboard = get_cancel_keyboard()
    bot.send_message(message.chat.id, "Начата процедура создания нового артиста, для отмены напишите 'Отмена'.", reply_markup=keyboard)
    send_next_question(bot, message)

