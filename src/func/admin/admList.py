from telebot import TeleBot
from ..db.dbAction import DB
import os
from .isWhitelist import is_user_allowed  # Изменен импорт

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')

def setup_admList_handler(bot: TeleBot, message):
    db = DB(db_path)
    handle_list_command(bot, message, db)

def handle_list_command(bot: TeleBot, message, db: DB):
    try:
        albums = db.get_all_albums()
        if albums:
            reply_message = "Список всех альбомов:\n"
            for album in albums:
                # Получение статуса модерации для текущего альбома
                moderation_status = db.check_moderation_status(album[0])
                if moderation_status is not None:
                    # Определение статуса модерации
                    if moderation_status == -1:
                        moderation_text = "Отклонен"
                    elif moderation_status == 0:
                        moderation_text = "На модерации"
                    elif moderation_status == 1:
                        moderation_text = "Отправлен на дистрибьюцию"
                    else:
                        moderation_text = "Неизвестный статус"
                else:
                    moderation_text = "Статус не найден"

                # Формирование строки с сокращенной информацией об альбоме
                album_info = f"ID: {album[0]}, Название: {album[1]}, Исполнитель: {album[2]}, Статус модерации: {moderation_text}\n"
                reply_message += album_info
            bot.reply_to(message, reply_message)
        else:
            bot.reply_to(message, "В базе данных пока нет альбомов.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при получении списка альбомов: {e}")