from telebot.types import Message

CHAT_ID_SUPPORT = '-1002082264985'

def setup_support_handler(bot):
    @bot.message_handler(func=lambda message: message.text == 'Поддержка')
    def handle_support(message: Message):
        # Запрашиваем вопрос у пользователя
        answer_text = "Введите вопрос для команды поддержки: "
        bot.send_message(chat_id=message.chat.id, text=answer_text)

        # Устанавливаем обработчик следующего сообщения пользователя
        @bot.message_handler(func=lambda m: m.from_user.id == message.chat.id)
        def handle_support_question(message):
            user_question = message.text

            # Отправляем информацию в чат поддержки
            support_message = f"Пользователь {message.chat.first_name} {message.chat.last_name} с ID {message.chat.id} отправил вопрос: {user_question}"
            bot.send_message(CHAT_ID_SUPPORT, support_message)

            # Отвечаем пользователю подтверждением
            confirmation_text = "Ваш вопрос отправлен в поддержку. Мы просматриваем каждый вопрос и ответим вам в ближайшее время."
            bot.send_message(message.chat.id, confirmation_text)

            # Завершаем обработку сообщения
            return
