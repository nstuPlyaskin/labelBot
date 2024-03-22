from telebot import TeleBot, types
from telebot.types import Message
from ..db.dbAction import DB
from ..shared.keyboard import get_cancel_keyboard, get_existing_artist_keyboard, get_main_keyboard, get_confirmation_keyboard

import os

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')

# Переменные для хранения вопросов и соответствующих им ключей
questions = [
    "Введите никнейм артиста:",
    "Есть ли артисты на фите?",
    "Введите название релиза:",
    "Введите дату релиза в формате DD.MM.YYYY (Пример 21.07.2024):",
    "Введите жанр релиза:",
    "Введите тайминг для коротких видео (shorts, reels, tiktok и др) в формате минут и секунд. Пример '0.35' или '1.34':",
    "Есть ли в треке ненормативная лексика?",
    "Желаете добавить текст песни?",
    "Оставьте ссылку с файлообменника YandexDisk или DropBox на ваш релиз (Обложка формата jpg размером от 2000х2000, без использования сторонней интеллектуальной собственности включая торговые марки, персонажей мультфильмов, игр, фильмов и так далее по аналогии) и (Аудио только WAV формат, стерео, , частота дискретизации - 44100 Гц):"
]

confrimQuestions = [
    "Никнейм артиста:", 
    "Есть артисты на фите:",
    "Название релиза:",
    "Дата релиза:",
    "Жанр релиза:",
    "Тайминг для коротких видео:",
    "Ненормативная лексика в треке:",
    "Добавить текст песни:",
    "Ссылка на релиз:"
]

keys = ["artistNickName", "feat", "releaseName", "releaseDate", "releaseGenre", "releaseTiming", "releaseExplicit", "releaseLyrics", "releaseLinkFiles"]

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
        bot.send_message(message.chat.id, "Создание релиза отменено.", reply_markup=get_main_keyboard())
        del user_states[user_id]
        return
    
    current_key = keys[current_question_index]
    user_answer = message.text.strip()
    
    if current_key == "artistNickName":
        # Проверяем существование артиста
        db = DB(db_path)
        if not db.check_artist_exists(user_answer):
            bot.send_message(message.chat.id, "Такого артиста не существует. Пожалуйста, выберите артиста из списка.")
            bot.send_message(message.chat.id, "Выберите артиста из списка:", reply_markup=get_existing_artist_keyboard())
            return
        else:
            user_data['artistID'] = db.get_artist_id(user_answer)  # Получаем ID артиста
            user_data['artistNickName'] = user_answer
    
    elif current_key == "feat":
        # Проверяем, есть ли артисты на фите
        if message.text.strip().lower() == "да":
            bot.send_message(message.chat.id, "Введите никнейм артистов на фите через запятую. Пример: Lil peep, Lil rip")
            bot.register_next_step_handler(message, save_feat_answer, bot=bot)
            return
    
    user_data[current_key] = user_answer
    questions_summary.append(f"{questions[current_question_index]} {user_answer}")
    current_question_index += 1
    user_states[user_id]['current_question_index'] = current_question_index
    user_states[user_id]['user_data'] = user_data
    user_states[user_id]['questions_summary'] = questions_summary
    send_next_question(bot, message)

# Функция для сохранения ответа пользователя на вопрос о фите артистов
def save_feat_answer(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_data = user_states[user_id]['user_data']
    feat_artists = [artist.strip() for artist in message.text.split(',')]
    user_data['feat'] = feat_artists
    send_next_question(bot, message)

# Функция для отправки сообщения с подтверждением введенной информации
def send_confirmation_message(bot, message):
    # Получаем данные пользователя из user_states
    user_id = message.from_user.id
    user_data = user_states[user_id]['user_data']
    
    # Проверяем, получены ли данные пользователя
    if user_data:
        # Формируем сообщение с подтверждением
        confirmation_text = "Пожалуйста, подтвердите введенные данные:\n\n"
        for key, value in user_data.items():
            if key in keys:
                confirmation_text += f"{confrimQuestions[keys.index(key)]} {value}\n"
        
        confirmation_text += "\nДанные корректны? (Да/Нет)"
        
        # Отправляем сообщение с подтверждением
        bot.send_message(chat_id=message.chat.id, text=confirmation_text, reply_markup=get_confirmation_keyboard())
        
        # Регистрируем обработчик ответа на подтверждение
        bot.register_next_step_handler(message, handle_confirmation_response, bot)
    else:
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, свяжитесь с администратором для помощи.")


# Функция для обработки ответа пользователя на подтверждение информации
def handle_confirmation_response(message: Message, bot: TeleBot):
    uid = message.from_user.id
    user_data = user_states[uid]['user_data']
    
    if message.text.lower() == "да":
        # Записываем данные в базу данных
        db = DB(db_path)
        success = db.saveRelease(user_data)
        db.close()

        if success:
            bot.send_message(message.chat.id, "Релиз успешно добавлен.")
        else:
            bot.send_message(message.chat.id, "Произошла ошибка при добавлении релиза.")
        
        # Удаляем данные пользователя из user_states
        del user_states[uid]
    elif message.text.lower() == "нет":
        # Пользователь хочет изменить информацию, начинаем процесс сначала
        del user_states[uid]
        setup_addRelease_handler(bot, message)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите 'Да' или 'Нет'.")

# Функция для начала процедуры создания нового релиза
def setup_addRelease_handler(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    user_states[user_id] = {'current_question_index': 0, 'user_data': {}, 'questions_summary': []}
    keyboard = get_cancel_keyboard()
    bot.send_message(message.chat.id, "Начата процедура создания нового релиза, для отмены напишите 'Отмена'.", reply_markup=keyboard)
    send_next_question(bot, message)

