from telebot import types

# Функция для получения клавиатуры с кнопкой "Добавить артиста"
def get_add_artist_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_add_artist = types.KeyboardButton(text="Добавить артиста")
    keyboard.add(button_add_artist)
    return keyboard

# Функция для получения клавиатуры с кнопками "Информация об артисте" и "Загрузить новый релиз"
def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btnArtistInfo = types.KeyboardButton('Информация об артисте')
    btnAddRelease = types.KeyboardButton('Загрузить новый релиз')
    btnSupport = types.KeyboardButton('Поддержка')
    keyboard.add(btnArtistInfo, btnAddRelease)
    keyboard.row(btnSupport)
    return keyboard

# Функция для получения клавиатуры с кнопками "Список артистов" и "Список релизов"
def get_existing_artist_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_list_artists = types.KeyboardButton(text="Список артистов")
    button_add_artist = types.KeyboardButton("Добавить артиста")

    button_main_keyboard = types.KeyboardButton(text="Вернуться в меню")
    keyboard.add(button_list_artists, button_add_artist, button_main_keyboard)
    return keyboard

# Функция для получения клавиатуры с кнопкой "Отмена"
def get_cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_cancel = types.KeyboardButton(text="Отмена")
    keyboard.add(button_cancel)
    return keyboard
