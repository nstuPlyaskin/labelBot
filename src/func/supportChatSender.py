from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from func.dbAction import DB
import os

#todo fix cancel button  

db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'support')
conn = None  # Объявляем переменную conn

already_sent_error = False

# Список команд для управления
MANAGEMENT_COMMANDS = ['Информация об артисте', 'Загрузить новый релиз']

def is_management_command(text):
    # Проверяем, является ли текст командой для управления
    return text.lower() in [command.lower() for command in MANAGEMENT_COMMANDS]

def setup_support_handler(bot):
    # Создаем словарь для отслеживания статуса обработки вопроса для каждого пользователя
    awaiting_question = {}

    @bot.message_handler(func=lambda message: message.text == 'Поддержка')
    def handle_support(message: Message):
        # Проверяем, не ждем ли мы уже вопрос от этого пользователя
        if awaiting_question.get(message.chat.id, False):
            # Если пользователь решил отменить отправку в поддержку
            awaiting_question.pop(message.chat.id, None)
            bot.send_message(message.chat.id, "Отправка в поддержку отменена.")
            return

        # Отмечаем, что начали ожидать вопрос от этого пользователя
        awaiting_question[message.chat.id] = True

        # Создаем клавиатуру с кнопкой "Отмена"
        cancel_button = InlineKeyboardButton("Отмена", callback_data="cancel")
        keyboard = InlineKeyboardMarkup().add(cancel_button)

        # Запрашиваем вопрос у пользователя
        answer_text = "Введите вопрос для команды поддержки или отправьте скриншот:"
        msg = bot.send_message(chat_id=message.chat.id, text=answer_text, reply_markup=keyboard)

        # Сохраняем идентификатор сообщения с клавиатурой "Отмена" для последующего редактирования
        awaiting_question[message.chat.id] = msg.message_id

    @bot.message_handler(content_types=[types.ContentType.TEXT, types.ContentType.PHOTO])
    def handle_support_question(message):
        # Проверяем, ожидает ли пользователь ответа в поддержку
        if awaiting_question.get(message.chat.id, False):
            process_support_question(message, awaiting_question)
        else:
            # Обработка обычных сообщений, не связанных с поддержкой
            pass

    def process_support_question(message, awaiting_question):
        user_question = None  # Инициализируем переменную для текстовой части (если есть)
        photo_id = None  # Инициализируем переменную для идентификатора фото (если есть)

        if message.content_type == 'text':
            user_question = message.text
            if not is_management_command(user_question):  # Исправление: проверка на команду для управления
                pass  # Мы уже сохраняем текст в базу данных ниже
            else:
                bot.send_message(message.chat.id, "Извините, но эта команда не может быть отправлена в поддержку. Для отмены нажмите повторно на 'Поддержка' в меню чата.")
                return

        if message.content_type == 'photo':

            if message.media_group_id:
                bot.send_message(message.chat.id, "Извините, но вы можете отправить только одно фото в поддержку. Для отмены нажмите повторно на 'Поддержка' в меню чата.")
                return
            pass

            # Получаем идентификатор фото
            photo_id = message.photo[-1].file_id

        # Очищаем флаг ожидания вопроса
        awaiting_question[message.chat.id] = False

        # ADD TO DB HERE
        db_handler = DB(db_path)

        # Сохраняем текст и/или фото в базу данных
        db_handler.addQuestion(bot, message)

        db_handler.close()

        bot.send_message(message.chat.id, "Ваш вопрос отправлен в поддержку. Мы просматриваем каждый вопрос и ответим вам в ближайшее время.")


    def send_support_photo_message(message):
        # Здесь можно добавить код для отправки сообщения с фото в поддержку
        pass

    @bot.callback_query_handler(func=lambda call: call.data == "cancel")
    def cancel_support(call):
        # Если пользователь нажал "Отмена" во время запроса в поддержку
        awaiting_question.pop(call.message.chat.id, None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Отправка в поддержку отменена.")

    # Завершаем обработку сообщения
    return
