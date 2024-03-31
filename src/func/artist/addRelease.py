from telebot import TeleBot, types
from telebot.types import Message
from ..db.dbAction import DB
from ..shared.keyboard import get_cancel_keyboard, get_existing_artist_keyboard, get_main_keyboard, get_confirmation_keyboard, get_confirmation_and_cancel_keyboard
from ..artist.addArtist import setup_addArtist_handler
import json
import os

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')
whitelist_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'whitelist.json')
text_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'texts.json')

# Загрузка текстов из файла texts.json
with open(text_path, 'r', encoding='utf-8') as file:
    texts = json.load(file)

addReleaseQuestions = texts["addReleaseQuestions"]
addReleaseConfirmationQuestions = texts["addReleaseConfirmationQuestions"]


keys = ["artistNickName", "feat", "releaseName", "releaseDate", "releaseGenre", "releaseTiming", "releaseExplicit", "releaseLyrics", "releaseLinkFiles"]

user_states = {}

def send_notification(bot: TeleBot, message: str):
    # Загрузка списка пользователей из whitelist
    allowed_users = load_whitelist()
    
    # Отправка уведомления каждому пользователю из whitelist
    for user_id in allowed_users:
        try:
            bot.send_message(user_id, message)
        except Exception as e:
            print(f"Ошибка отправки уведомления пользователю {user_id}: {str(e)}")

def load_whitelist():
    with open(whitelist_path, 'r', encoding='utf-8') as file:
        whitelist_data = json.load(file)
        allowed_users = whitelist_data.get("allowed_users", [])
        return allowed_users

def send_next_question(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    if user_id not in user_states:
        user_states[user_id] = {'current_question_index': 0, 'user_data': {}, 'questions_summary': []}
        
    current_question_index = user_states[user_id]['current_question_index']
    user_data = user_states[user_id]['user_data']
    questions_summary = user_states[user_id]['questions_summary']
    
    if current_question_index < len(addReleaseQuestions):
        keyboard = None  # No keyboard by default
        
        # Check if it's the question about selecting an artist
        if current_question_index == 0:
            # Get user's artist nicknames from the database
            db = DB(db_path)
            artist_nicknames = db.get_user_artists(user_id)
            db.close()
            
            # Create a keyboard with artist nicknames
            keyboard_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            for nickname in artist_nicknames:
                keyboard_markup.add(nickname)
            
            # Add "Отмена" button to the keyboard
            keyboard_markup.row(types.KeyboardButton("Отмена"))
            
            # Assign the created keyboard to the 'keyboard' variable
            keyboard = keyboard_markup
        else:
            # Determine the keyboard based on the current question index
            keyboard = get_confirmation_and_cancel_keyboard() if current_question_index == 6 else get_cancel_keyboard()

        
        bot.send_message(message.chat.id, addReleaseQuestions[current_question_index], reply_markup=keyboard)
        bot.register_next_step_handler(message, save_user_answer, bot=bot)
    else:
        send_confirmation_message(bot, message)

def save_user_answer(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    current_question_index = user_states[user_id]['current_question_index']
    user_data = user_states[user_id]['user_data']
    questions_summary = user_states[user_id]['questions_summary']
    
    if message.text.strip().lower() == "отмена":
        bot.send_message(message.chat.id, "Создание релиза отменено.", reply_markup=get_main_keyboard())
        del user_states[user_id]
        return
    
    current_key = keys[current_question_index]
    user_answer = message.text.strip()
    
    if current_key == "artistNickName":
        db = DB(db_path)
        if not db.check_artist_exists(user_answer):
            bot.send_message(message.chat.id, "Такого артиста не существует. Пожалуйста, выберите артиста из списка.")
            bot.send_message(message.chat.id, "Выберите артиста из списка:", reply_markup=get_existing_artist_keyboard())
            return
        else:
            user_data['artistID'] = db.get_artist_id(user_answer)
            user_data['artistNickName'] = user_answer
    
    elif current_key == "feat":
        if message.text.strip().lower() == "да":
            bot.send_message(message.chat.id, "Введите никнейм артистов на фите через запятую.\nПример: artist name one, artist name two")
            bot.register_next_step_handler(message, save_feat_answer, bot=bot)
            return
    
    user_data[current_key] = user_answer
    questions_summary.append(f"{addReleaseQuestions[current_question_index]} {user_answer}")
    current_question_index += 1
    user_states[user_id]['current_question_index'] = current_question_index
    user_states[user_id]['user_data'] = user_data
    user_states[user_id]['questions_summary'] = questions_summary
    send_next_question(bot, message)

def save_feat_answer(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_data = user_states[user_id]['user_data']
    feat_artists = [artist.strip() for artist in message.text.split(',')]
    user_data['feat'] = feat_artists
    send_next_question(bot, message)

def send_confirmation_message(bot, message):
    user_id = message.from_user.id
    user_data = user_states[user_id]['user_data']
    
    if user_data:
        confirmation_text = "Пожалуйста, подтвердите введенные данные:\n\n"
        for key, value in user_data.items():
            if key in keys:
                confirmation_text += f"{addReleaseConfirmationQuestions[keys.index(key)]} {value}\n"
        
        confirmation_text += "\nДанные корректны? (Да/Нет)"
        
        bot.send_message(chat_id=message.chat.id, text=confirmation_text, reply_markup=get_confirmation_keyboard())
        
        bot.register_next_step_handler(message, handle_confirmation_response, bot)
    else:
        bot.reply_to(message, "Произошла ошибка, сообщите в поддержку")

def handle_confirmation_response(message: Message, bot: TeleBot):
    uid = message.from_user.id
    user_data = user_states[uid]['user_data']
    
    # Проверяем, что пользователь ввел "Да" или "Нет"
    if message.text.lower() == "да":
        db = DB(db_path)
        
        # Проверяем, существует ли релиз с таким именем у артиста
        existing_release = db.get_release_by_name(user_data["artistNickName"], user_data["releaseName"])
        if existing_release:
            bot.send_message(message.chat.id, "Релиз с таким именем уже существует. Пожалуйста, введите другое имя.")
            # Запускаем процесс создания релиза заново
            setup_addRelease_handler(bot, message)
            return
        
        # Ваша логика сохранения релиза в базе данных
        success = db.saveRelease(user_data)
        db.close()

        if success:
            bot.send_message(message.chat.id, "Релиз успешно добавлен.", reply_markup=get_main_keyboard())
            send_notification(bot, "В базе данных появился новый релиз на модерации")
        else:
            bot.send_message(message.chat.id, "Произошла ошибка при добавлении релиза.", reply_markup=get_main_keyboard())
        
        del user_states[uid]  # Удаляем состояние пользователя из словаря после завершения процесса
    elif message.text.lower() == "нет":
        del user_states[uid]  # Пользователь отказался от добавления релиза, удаляем состояние пользователя
        setup_addRelease_handler(bot, message)  # Начинаем процесс сначала
    else:
        # Ожидаем следующего сообщения снова от пользователя
        bot.register_next_step_handler(message, handle_confirmation_response, bot)
        bot.send_message(message.chat.id, "Пожалуйста, введите 'Да' или 'Нет'.")



def setup_addRelease_handler(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    db = DB(db_path)
    
    # Проверяем, есть ли у пользователя хотя бы один артист в базе данных
    if not db.get_user_artists(user_id):
        # Если у пользователя нет артистов, открываем форму создания артиста
        bot.send_message(message.chat.id, "Для создания релиза сначала нужно добавить артиста.")
        setup_addArtist_handler(bot, message)
        return

    user_states[user_id] = {'current_question_index': 0, 'user_data': {}, 'questions_summary': []}
    keyboard = get_cancel_keyboard()
    bot.send_message(message.chat.id, "Начата процедура создания нового релиза, для отмены напишите 'Отмена'.", reply_markup=keyboard)
    send_next_question(bot, message)
