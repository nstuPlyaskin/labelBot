from telebot import types
from telebot.types import Message
from telebot import TeleBot

def setup_artistInfo_handler(bot: TeleBot):
    @bot.message_handler(func=lambda message: message.text == 'Информация об артисте')
    def handle_support(message: Message):
        answerText = "обработка инфо по артисту"
        bot.send_message(chat_id=message.chat.id, text=answerText)
