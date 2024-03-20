import sqlite3
import os

# # Получаем абсолютный путь к файлу базы данных
db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'support')

#     # ПРИМЕР ВЫВОДА ИЗОБРАЖЕНИЯ
#     # file_id = "AgACAgIAAxkBAAIOJmX64yoV2HZ0t9FCVRaf45YwE8VmAAIO1jEbjpbYS9Na8qN5uHGQAQADAgADeQADNAQ"
#     # bot.send_photo(message.chat.id, file_id)


class DB:
    #init db
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    # add records into db
    def addQuestion(self, message):
         # Получаем информацию о сообщении
        
        uid = message.from_user.id
        userName = message.from_user.username
        userQuestion = message.caption if message.caption else (message.text if message.text else "")
        userMedia = message.photo[-1].file_id if message.photo else ""


        self.cursor.execute("INSERT INTO supportTable (uid, userName, userQuestion, userMedia) VALUES (?, ?, ?, ?)",
                       (uid, userName, userQuestion, userMedia))
        
        print("ADDED NEW QUESTION: \n uid: ", uid, "userName: ", userName, "userQuestion: ", userQuestion, "userMedia: ", userMedia)
        return self.conn.commit()

    def close (self):
        self.conn.close()