from telebot import types
from telebot.types import Message
from telebot import TeleBot

def setup_support_handler(bot: TeleBot):
    @bot.message_handler(func=lambda message: message.text == 'Поддержка')
    def handle_support(message: Message):
        answerText = "обработка поддержки"
        bot.send_message(chat_id=message.chat.id, text=answerText)
