import telebot
from func.admin import admQuestions, admAnswer, admUserList, admMessage
from func.artist import addArtist, addRelease, artistInfo, artistList
from func.shared.keyboard import get_main_keyboard
from func.support import supportChatSender

bot = telebot.TeleBot('6966429364:AAHvq_OtGRezUpEjje_RlIGPFV7b9PprR1w') 

@bot.message_handler(commands=['start', 'help', 'menu'])
def handle_start(message):
    bot.send_message(chat_id=message.chat.id, text='Выберите опцию:', reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == "Добавить артиста")
def handle_add_artist(message):
    addArtist.setup_addArtist_handler(bot, message)

@bot.message_handler(func=lambda message: message.text in ["Список артистов", "Информация об артисте"])
def handle_list_artists(message):
    if message.text == "Список артистов":
        artistList.setup_artistList_handler(bot, message)
    else:
        artistInfo.setup_artistInfo_handler(bot, message)

@bot.message_handler(func=lambda message: message.text == "Список релизов")
def handle_list_releases(message):
    print("Кнопка 3")

@bot.message_handler(func=lambda message: message.text == "Вернуться в меню")
def handle_openMenu_releases(message):
    bot.send_message(chat_id=message.chat.id, text='Выберите опцию:', reply_markup=get_main_keyboard())

@bot.message_handler(commands=['questions', 'q'])
def handle_questions(message):
    admQuestions.setup_admQuestions_handler(bot, message)

@bot.message_handler(commands=['answer', 'a'])
def handle_answer(message):
    admAnswer.setup_admAnswer_handler(bot, message)

@bot.message_handler(commands=['users', 'u'])
def setup_admUserList_handler(message):
    admUserList.setup_admUserList_handler(bot, message)

@bot.message_handler(commands=['message', 'm'])
def setup_admMsg_handler(message):
    admMessage.setup_admMsg_handler(bot, message)

@bot.message_handler(commands=['artistInfo', 'artist', 'info', 'information', 'inf', 'stat', 'stats'])
def setup_artistInfo_handler(message):
    artistInfo.setup_artistInfo_handler(bot, message)

supportChatSender.setup_support_handler(bot)
addRelease.setup_addRelease_handler(bot)

bot.polling(none_stop=True)
