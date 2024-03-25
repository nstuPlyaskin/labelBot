from telebot import TeleBot
import os
from .isWhitelist import is_user_allowed
from ..db.dbAction import DB

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')

# В функции moderate_releases из файла admModerate.py добавим проверку на isModerated
def moderate_releases(bot: TeleBot, message):
    if is_user_allowed(message.from_user.id):
        args = message.text.split()
        if len(args) > 1:  
            release_id = args[1]  
            db = DB(db_path)
            
            # Проверяем значение поля isModerated для релиза
            is_moderated = db.check_moderation_status(release_id)
            
            if is_moderated == 1:
                bot.send_message(message.chat.id, "Этот релиз уже отмодерирован и его статус нельзя изменить.")
                return
            
            release_details = db.get_release_details(release_id)

            if release_details:
                if len(args) > 2 and args[2] in ['accept', 'reject']:
                    if args[2] == 'accept':
                        db.approve_release(release_id, bot)
                    elif args[2] == 'reject':
                        db.reject_release(release_id, bot)
                else:
                    release_message = "Детали релиза:\n\n"
                    for key, value in release_details.items():
                        release_message += f"{key}: {value}\n"
                    bot.send_message(message.chat.id, release_message)
            else:
                bot.send_message(message.chat.id, "Релиз с указанным ID не найден.")
            
            db.close()  # Закрываем соединение с базой данных после использования
        else:
            bot.reply_to(message, "Пожалуйста, укажите ID релиза после команды.")
    else:
        bot.reply_to(message, "Извините, у вас нет доступа к этой команде.")
