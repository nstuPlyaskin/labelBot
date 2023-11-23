from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

CHAT_ID_SUPPORT = '-1002082264985'

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

        if message.content_type == 'text':
            user_question = message.text
            if not is_management_command(user_question):  # Исправление: проверка на команду для управления
                send_support_text_message(message, user_question)
            else:
                bot.send_message(message.chat.id, "Извините, но эта команда не может быть отправлена в поддержку. Для отмены нажмите повторно на 'Поддержка' в меню чата.")
                return
        elif message.content_type == 'photo':
            # Обрабатываем отправленное фото
            user_question = "\n"
            send_support_photo_message(message, user_question)

        # Очищаем флаг ожидания вопроса
        awaiting_question[message.chat.id] = False
        bot.send_message(message.chat.id, "Ваш вопрос отправлен в поддержку. Мы просматриваем каждый вопрос и ответим вам в ближайшее время.")

    def send_support_text_message(message, user_question):
        # Truncate the message if it exceeds the maximum allowed length
        max_message_length = 4096  # Telegram API maximum message length
        if len(user_question) > max_message_length:
            user_question = user_question[:max_message_length]

        support_message = f"Пользователь {message.chat.first_name} {message.chat.last_name} (UID {message.chat.id}) отправил вопрос: {user_question}"
        bot.send_message(CHAT_ID_SUPPORT, support_message)

    def send_support_photo_message(message, user_question):
        # Отправляем фото в чат поддержки
        photo_id = message.photo[-1].file_id  # Получаем ID файла последней фотографии (по умолчанию отправляется самая большая)
        support_message = f"Пользователь {message.from_user.first_name} {message.from_user.last_name} (ID {message.from_user.id}) отправил вопрос:"

        # Проверяем, есть ли текст (caption) у фото
        if message.caption:
            user_question += f"\nТекст: {message.caption}"

        # Добавляем текстовую часть к сообщению перед отправкой фото
        support_message += f"\n{user_question}"

        bot.send_photo(CHAT_ID_SUPPORT, photo_id, caption=support_message)

    @bot.callback_query_handler(func=lambda call: call.data == "cancel")
    def cancel_support(call):
        # Если пользователь нажал "Отмена" во время запроса в поддержку
        awaiting_question.pop(call.message.chat.id, None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Отправка в поддержку отменена.")

    # Завершаем обработку сообщения
    return
