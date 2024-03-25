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
    btnAddRelease = types.KeyboardButton('Информация о релизах')
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


# Функция для получения клавиатуры с кнопками "Список артистов" и "Список релизов"
def get_existing_releases_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_list_releases = types.KeyboardButton(text="Список релизов")
    button_add_release = types.KeyboardButton("Добавить релиз")

    button_main_keyboard = types.KeyboardButton(text="Вернуться в меню")
    keyboard.add(button_list_releases, button_add_release, button_main_keyboard)
    return keyboard

# Функция для получения клавиатуры с кнопкой "Отмена"
def get_cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_cancel = types.KeyboardButton(text="Отмена")
    keyboard.add(button_cancel)
    return keyboard

def get_confirmation_and_cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_yes = types.KeyboardButton("Да")
    button_no = types.KeyboardButton("Нет")
    button_cancel = types.KeyboardButton("Отмена")
    keyboard.add(button_yes, button_no)
    keyboard.row(button_cancel)
    return keyboard

def get_confirmation_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_yes = types.KeyboardButton("Да")
    button_no = types.KeyboardButton("Нет")
    keyboard.add(button_yes, button_no)
    return keyboard

def moderate_release_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_accepted = types.KeyboardButton("Релиз одобрен к дистрибуции")
    button_rejected = types.KeyboardButton("Отклонить релиз")
    button_cancel = types.KeyboardButton("Отмена")
    keyboard.add(button_accepted, button_rejected)
    keyboard.row(button_cancel)
    return keyboard
    
