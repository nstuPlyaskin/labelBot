import telebot
from telebot import types
from func import artistInfo, addRelease, supportChatSender, admQuestions, admAnswer, admUserList, admMessage
  # Импортируем файл с обработчиками поддержки из подпапки func

bot = telebot.TeleBot('6966429364:AAHvq_OtGRezUpEjje_RlIGPFV7b9PprR1w') 

@bot.message_handler(commands=['start', 'help', 'menu'])
def handle_start(message):
    # Создаем клавиатуру
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    # Создаем две колонки с кнопками
    btnArtistInfo = types.KeyboardButton('Информация об артисте')
    btnAddRelease = types.KeyboardButton('Загрузить новый релиз')

    # Добавляем кнопки в первую колонку
    keyboard.add(btnArtistInfo, btnAddRelease)

    # Создаем кнопку "Поддержка" и добавляем в новую строку
    btnSupport = types.KeyboardButton('Поддержка')
    keyboard.row(btnSupport)

    # Отправляем сообщение с клавиатурой
    bot.send_message(chat_id=message.chat.id, text='Выберите опцию:', reply_markup=keyboard)

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

# Вызываем функцию для настройки обработчика поддержки
supportChatSender.setup_support_handler(bot)

# Вызываем функцию для настройки обработчика инфо по артисту
artistInfo.setup_artistInfo_handler(bot)

# Вызываем функцию для настройки обработчика инфо по артисту
addRelease.setup_addRelease_handler(bot)

# Запускаем бота
bot.polling(none_stop=True)