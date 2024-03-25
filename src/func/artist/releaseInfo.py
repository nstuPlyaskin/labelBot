from telebot import TeleBot
from func.shared.keyboard import get_existing_releases_keyboard

def setup_releaseInfo_handler(bot: TeleBot, message):

    bot.reply_to(message, "Выберите опцию:", reply_markup=get_existing_releases_keyboard())
