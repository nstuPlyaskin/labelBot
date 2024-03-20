import sqlite3
import os

# Получаем абсолютный путь к файлу базы данных
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

        # Запись в бд
        self.cursor.execute("INSERT INTO supportTable (uid, userName, userQuestion, userMedia) VALUES (?, ?, ?, ?)",
                       (uid, userName, userQuestion, userMedia))
        
        print("ADDED NEW QUESTION: \n uid: ", uid, "userName: ", userName, "userQuestion: ", userQuestion, "userMedia: ", userMedia)
        return self.conn.commit()
    
    def showQuestions(self, bot, message):
        self.cursor.execute("SELECT id, userName, userQuestion, userMedia, date FROM supportTable WHERE isActual = 1")
        rows = self.cursor.fetchall()
        for row in rows:
            id, username, question, usermedia, date = row
            # Отправляем сообщение с подписью к изображению, если userMedia не пустое
            if usermedia:
                bot.send_photo(chat_id=message.chat.id, photo=usermedia, caption=f"Вопрос №{id} от пользователя: {username}\n\nQuestion: {question}\n\nВопрос был задан {date}")
            # Иначе отправляем текстовое сообщение
            else:
                bot.send_message(chat_id=message.chat.id, text=f"Вопрос №{id} от пользователя: {username}\n\nQuestion: {question}\n\nВопрос был задан {date}")


    def close (self):
        self.conn.close()