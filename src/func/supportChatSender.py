from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

CHAT_ID_SUPPORT = '-1002082264985'

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
        bot.send_message(chat_id=message.chat.id, text=answer_text, reply_markup=keyboard)

    @bot.message_handler(func=lambda m: awaiting_question.get(m.from_user.id, False))
    def handle_support_question(message):
        user_question = message.text

        # Отправляем информацию в чат поддержки
        support_message = f"Пользователь {message.chat.first_name} {message.chat.last_name} с ID {message.chat.id} отправил вопрос: {user_question}"
        bot.send_message(CHAT_ID_SUPPORT, support_message)

        # Отвечаем пользователю подтверждением
        confirmation_text = "Ваш вопрос отправлен в поддержку. Мы просматриваем каждый вопрос и ответим вам в ближайшее время."
        bot.send_message(message.chat.id, confirmation_text)

        # Сбрасываем статус ожидания для этого пользователя
        awaiting_question.pop(message.chat.id, None)

    @bot.callback_query_handler(func=lambda call: call.data == "cancel")
    def cancel_support(call):
        # Если пользователь нажал "Отмена" во время запроса в поддержку
        awaiting_question.pop(call.message.chat.id, None)
        bot.send_message(call.message.chat.id, "Отправка в поддержку отменена.")

    # Завершаем обработку сообщения
    return
