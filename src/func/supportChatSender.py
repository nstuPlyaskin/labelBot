from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

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
        answer_text = "Введите вопрос для команды поддержки или нажмите 'Отмена' для отмены:"
        msg = bot.send_message(chat_id=message.chat.id, text=answer_text, reply_markup=keyboard)

        # Сохраняем идентификатор сообщения с клавиатурой "Отмена" для последующего редактирования
        awaiting_question[message.chat.id] = msg.message_id

    @bot.message_handler(func=lambda m: awaiting_question.get(m.from_user.id, False))
    def handle_support_question(message):
        user_question = message.text

        # Проверяем, не является ли вопрос командой для управления
        if is_management_command(user_question):
            bot.send_message(message.chat.id, "Извините, но эта команда не может быть отправлена в поддержку. Для отмены используйте кнопку 'Отмена'")
            return

        # Проверяем, не является ли вопрос текстом "Отмена"
        if user_question.lower() == "отмена":
            # Если пользователь написал "Отмена", завершаем обработку запроса
            awaiting_question.pop(message.chat.id, None)
            bot.send_message(message.chat.id, "Отправка в поддержку отменена.")
            return

        # Отправляем информацию в чат поддержки
        support_message = f"Пользователь {message.chat.first_name} {message.chat.last_name} (ID {message.chat.id}) отправил вопрос: {user_question}"
        bot.send_message(CHAT_ID_SUPPORT, support_message)

        # Удаляем клавиатуру "Отмена" после успешной отправки запроса
        bot.edit_message_text(chat_id=message.chat.id, message_id=awaiting_question.pop(message.chat.id),
                              text="Ваш вопрос отправлен в поддержку. Мы просматриваем каждый вопрос и ответим вам в ближайшее время.")

    @bot.callback_query_handler(func=lambda call: call.data == "cancel")
    def cancel_support(call):
        # Если пользователь нажал "Отмена" во время запроса в поддержку
        awaiting_question.pop(call.message.chat.id, None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Отправка в поддержку отменена.")

    # Завершаем обработку сообщения
    return
