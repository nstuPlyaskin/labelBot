from telebot import types
from telebot.types import Message
from telebot import TeleBot

def setup_addRelease_handler(bot: TeleBot):
    @bot.message_handler(func=lambda message: message.text == 'Загрузить новый релиз')
    def handle_support(message: Message):
        answerText = "обработка новый релиз"
        bot.send_message(chat_id=message.chat.id, text=answerText)
