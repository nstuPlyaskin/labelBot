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

        # Проверяем, существует ли релиз с указанным id
        if db.get_field_value(release_id, 'releaseID') is None:
            bot.send_message(message.chat.id, f"Релиза с id {release_id} нет.")
            return

        # Получаем предыдущее значение поля
        previous_value = db.get_field_value(release_id, field_name)
        # Получаем uid пользователя, который загрузил релиз
        uid = db.get_uid_by_release_id(release_id)

        # Проверяем, является ли измененное поле одним из тех, которые требуют уведомления
        notification_fields = ['artistNickName', 'feat', 'releaseName', 'releaseDate', 'releaseGenre', 'releaseLyrics', 'releaseLinkFiles']
        if field_name in notification_fields:
            # Обновляем поле в базе данных
            db.update_release_field(release_id, field_name, new_value)

            # Отправляем уведомление пользователю о изменении его релиза после успешного обновления
            notification = f"Модерация изменила данные в вашем релизе: {field_name} изменено с {previous_value if previous_value else 'None'} на {new_value}. Если вы не отправляли запрос на изменение данных, обратитесь в поддержку."
            bot.send_message(uid, notification)

            bot.reply_to(message, f"Поле '{field_name}' для релиза с ID {release_id} успешно обновлено.")
        else:
            # Если поле не требует уведомления, просто обновляем его без отправки уведомления пользователю
            db.update_release_field(release_id, field_name, new_value)
            bot.reply_to(message, f"Поле '{field_name}' для релиза с ID {release_id} успешно обновлено.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при обновлении поля: {e}")
