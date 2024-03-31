import telebot
from func.admin import admQuestions, admAnswer, admUserList, admMessage, admReleases, admModerate, admEdit, admList
from func.artist import addArtist, addRelease, artistInfo, artistList, addRelease, releaseInfo, releaseList, releasePromo
from func.shared.keyboard import get_main_keyboard
from func.shared.help import show_help_cmd
from func.support.supportChatSender import setup_support_handler

# @FIX HELP!!!
# @todo autobackup db - python file

# @todo /start создает бд с uid чела потом /u будем делать по этой таблице!!!

# @todo ошибка при обновлении данных в бд: бд выдает старые данные 
# @todo /u not from support to artist? - mb new table with all users

# @todo пусть /u выводит сначала админов (из вайтлиста)

bot = telebot.TeleBot('6966429364:AAHvq_OtGRezUpEjje_RlIGPFV7b9PprR1w') 

@bot.message_handler(commands=['start', 'menu'])
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

@bot.message_handler(func=lambda message: message.text == "Добавить релиз")
def handle_add_release(message):
    addRelease.setup_addRelease_handler(bot, message)  # Вызываем функцию для начала процедуры добавления нового релиза из addRelease.py

@bot.message_handler(func=lambda message: message.text == "Информация о релизах")
def handle_list_release(message):
    releaseInfo.setup_releaseInfo_handler(bot, message)  # Вызываем функцию для начала процедуры добавления нового релиза из addRelease.py

@bot.message_handler(func=lambda message: message.text == "Список релизов")
def handle_add_release(message):
    releaseList.setup_releaseList_handler(bot, message)  # Вызываем функцию для начала процедуры добавления нового релиза из addRelease.py

@bot.message_handler(func=lambda message: message.text == "Вернуться в меню")
def handle_openMenu_releases(message):
    bot.send_message(chat_id=message.chat.id, text='Выберите опцию:', reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == "Отправить на промо")
def handle_releasePromo(message):
    releasePromo.setup_releasePromo_handler(bot, message)  # Pass bot as an argument

@bot.message_handler(func=lambda message: message.text == "Поддержка")
def handle_support(message):
    support_handler = setup_support_handler(bot)  # Получаем функцию из модуля
    support_handler(message)  # Вызываем эту функцию, чтобы обработать сообщение

@bot.message_handler(commands=['question', 'questions', 'q'])
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

@bot.message_handler(commands=['releases', 'r'])
def show_unmoderated_releases(message):
    admReleases.show_unmoderated_releases(bot, message)

@bot.message_handler(commands=['moderate', 'mod'])
def moderate_releases(message):
    admModerate.moderate_releases(bot, message)

@bot.message_handler(commands=['edit', 'e'])
def moderate_releases(message):
    admEdit.setup_admEdit_handler(bot, message)

@bot.message_handler(commands=['list', 'l'])
def list_releases(message):
    admList.setup_admList_handler(bot, message)

@bot.message_handler(commands=['artist', 'info', 'stats'])
def setup_artistInfo_handler(message):
    artistInfo.setup_artistInfo_handler(bot, message)

@bot.message_handler(commands=['help', 'cmd', 'команды', 'кмд'])
def handle_start(message):
    show_help_cmd(bot, message)

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker'])
def handle_all_messages(message):
    bot.send_message(chat_id=message.chat.id, text='Извините, я не распознал ваш запрос, выберите опцию используя клавиатуру чат-бота.', reply_markup=get_main_keyboard())

bot.polling(none_stop=True)