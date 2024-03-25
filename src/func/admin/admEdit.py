from telebot import TeleBot
from ..db.dbAction import DB
import os
from .isWhitelist import is_user_allowed  # Изменен импорт

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')

def setup_admEdit_handler(bot: TeleBot, message):
    db = DB(db_path)
    handle_edit_command(bot, message, db)

def handle_edit_command(bot: TeleBot, message, db: DB):
    try:
        # Разбиваем сообщение на аргументы
        args = message.text.split()[1:]

        if len(args) < 3:
            bot.reply_to(message, "Неверное количество аргументов. Используйте /edit [id релиза] [поле] [новое значение]")
            return

        # Получаем аргументы
        release_id = int(args[0])
        field_name = args[1]
        new_value = ' '.join(args[2:])  # Объединяем оставшиеся аргументы в одну строку

        # Обновляем поле в базе данных
        db.update_release_field(release_id, field_name, new_value)
        bot.reply_to(message, f"Поле '{field_name}' для релиза с ID {release_id} успешно обновлено.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при обновлении поля: {e}")
