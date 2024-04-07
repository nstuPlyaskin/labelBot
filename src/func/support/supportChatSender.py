from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from ..db.dbAction import DB
from ..shared.keyboard import get_cancel_keyboard, get_main_keyboard
import os

#todo fix cancel button  

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')
conn = None  # Объявляем переменную conn

already_sent_error = False

# Список команд для управления
MANAGEMENT_COMMANDS = ['Информация об артисте', 'Загрузить новый релиз', 'Поддержка', 'Добавить артиста', 'Список артистов', 'Информация об артисте', 'Добавить релиз', 'Информация о релизах', 'Список релизов']

def is_management_command(text):
    # Проверяем, является ли текст командой для управления
    return text.lower() in [command.lower() for command in MANAGEMENT_COMMANDS]

def setup_support_handler(bot):
    # Создаем словарь для отслеживания статуса обработки вопроса для каждого пользователя
    awaiting_question = {}

    # Функция, вызываемая из main.py
    def handle_support(message):
        # Проверяем, не ждем ли мы уже вопрос от этого пользователя
        if awaiting_question.get(message.chat.id, False):
            # Если пользователь решил отменить отправку в поддержку
            awaiting_question.pop(message.chat.id, None)
            bot.send_message(message.chat.id, "Отправка в поддержку отменена.", reply_markup=get_main_keyboard())
            return


        # Отмечаем, что начали ожидать вопрос от этого пользователя
        awaiting_question[message.chat.id] = True

        # Запрашиваем вопрос у пользователя
        answer_text = "Введите вопрос для команды поддержки или отправьте скриншот:"
        msg = bot.send_message(chat_id=message.chat.id, text=answer_text, reply_markup=get_cancel_keyboard())  # Изменено здесь

        # Регистрируем следующий шаг для обработки ответа пользователя
        bot.register_next_step_handler(msg, handle_support_question)



    # Обработчик вопроса от пользователя
    def handle_support_question(message):
        user_question = message.text  # Получаем вопрос пользователя

        # Проверяем, если отправлена медиагруппа (несколько изображений)
        if message.media_group_id:
            bot.send_message(message.chat.id, "Отправлять можно только одно изображение. Пожалуйста, отправьте свой вопрос снова.")
            return

        # Проверяем, если сообщение не пустое и если это "Отмена", то не сохраняем его в базу данных
        if message.text and message.text.lower() == "отмена":
            awaiting_question.pop(message.chat.id, None)  # Отменяем ожидание вопроса
            bot.send_message(message.chat.id, "Отправка в поддержку отменена.", reply_markup=get_main_keyboard())
            return

        # Далее идет ваша обработка вопроса, сохранение в базу данных и отправка сообщения поддержке

        # Очищаем флаг ожидания вопроса
        awaiting_question[message.chat.id] = False

        # ADD TO DB HERE
        db_handler = DB(db_path)

        # Сохраняем текст и/или фото в базу данных
        db_handler.addQuestion(bot, message)

        db_handler.close()

        bot.send_message(message.chat.id, "Ваш вопрос отправлен в поддержку. Мы просматриваем каждый вопрос и ответим вам в ближайшее время.", reply_markup=get_main_keyboard())

    # Завершаем обработку сообщения
    return handle_support  # Возвращаем функцию для дальнейшего использования в main.py
