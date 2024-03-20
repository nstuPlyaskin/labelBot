import sqlite3
import os
import json
from telebot.apihelper import ApiTelegramException

# Получаем абсолютный путь к файлу базы данных
db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'support')
whitelist_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'whitelist.json')

#     # ПРИМЕР ВЫВОДА ИЗОБРАЖЕНИЯ
#     # file_id = "AgACAgIAAxkBAAIOJmX64yoV2HZ0t9FCVRaf45YwE8VmAAIO1jEbjpbYS9Na8qN5uHGQAQADAgADeQADNAQ"
#     # bot.send_photo(message.chat.id, file_id)


class DB:
    #init db
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    # add records into db
    def addQuestion(self, bot, message):
        # Получаем информацию о сообщении
        uid = message.from_user.id
        userName = message.from_user.username
        userQuestion = message.caption if message.caption else (message.text if message.text else "")
        userMedia = message.photo[-1].file_id if message.photo else ""

        # Запись в бд
        self.cursor.execute("INSERT INTO supportTable (uid, userName, userQuestion, userMedia) VALUES (?, ?, ?, ?)",
                    (uid, userName, userQuestion, userMedia))
        
        print("ADDED NEW QUESTION: \n uid: ", uid, "userName: ", userName, "userQuestion: ", userQuestion, "userMedia: ", userMedia)
        self.conn.commit()

        # Оповещение пользователей из whitelist.json о новом вопросе
        with open(whitelist_path, "r") as f:
            whitelist_data = json.load(f)
            allowed_users = whitelist_data.get("allowed_users", [])  # Получаем список разрешенных пользователей
            for user_id in allowed_users:
                try:
                    bot.send_message(chat_id=user_id, text="Появился новый вопрос в базе данных поддержки!")
                except ApiTelegramException as e:
                    print(f"Failed to send message to user {user_id}: {e}")
                    # Можно сделать что-то еще, например, отправить себе уведомление о проблеме
                    pass

        return
    
    def showQuestions(self, bot, message):
        # Получаем количество актуальных вопросов в базе данных
        self.cursor.execute("SELECT COUNT(*) FROM supportTable WHERE isActual = 1")
        total_questions = self.cursor.fetchone()[0]

        # Проверяем, есть ли вопросы в базе данных
        if total_questions > 0:
            # Выполняем запрос для получения последнего вопроса
            self.cursor.execute("SELECT id, userName, userQuestion, userMedia, date FROM supportTable WHERE isActual = 1 ORDER BY id DESC LIMIT 1")
            row = self.cursor.fetchone()
            id, username, question, usermedia, date = row

            # Отправляем сообщение с подписью к изображению, если userMedia не пустое
            if usermedia:
                bot.send_photo(chat_id=message.chat.id, photo=usermedia, caption=f"Вопрос №{id} от пользователя: {username}\n\nQuestion: {question}\n\nОсталось вопросов в очереди: {total_questions - 1}\nВопрос был задан {date}\n\nДля ответа используйте /answer (номер вопроса) и текст ответа.\nПример: /answer 69 Здравствуйте, я ответил на ваш вопрос.")
            # Иначе отправляем текстовое сообщение
            else:
                bot.send_message(chat_id=message.chat.id, text=f"Вопрос №{id} от пользователя: {username}\n\nQuestion: {question}\n\nОсталось вопросов в очереди: {total_questions - 1}\nВопрос был задан {date}\n\nДля ответа используйте /answer (номер вопроса) и текст ответа.\nПример: /answer 69 Здравствуйте, я ответил на ваш вопрос.")
        else:
            bot.send_message(chat_id=message.chat.id, text="На данный момент вопросов нет.")


    def getAnswer(self, bot, message):
        # Разбиваем сообщение на аргументы (номер вопроса и текст ответа)
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            bot.reply_to(message, "Вы должны указать номер вопроса и текст ответа. Пример: /answer 69 Здравствуйте, я ответил на ваш вопрос.")
            return

        # Получаем номер вопроса и текст ответа из аргументов
        question_id = args[1]
        answer_text = args[2]

        # Проверяем, существует ли вопрос с указанным номером
        self.cursor.execute("SELECT * FROM supportTable WHERE id = ? AND isActual = 1", (question_id,))
        question = self.cursor.fetchone()
        if question:
            # Обновляем запись в базе данных с ответом на вопрос и помечаем вопрос как отвеченный
            self.cursor.execute("UPDATE supportTable SET userAnswer = ?, isActual = 0 WHERE id = ?", (answer_text, question_id))
            self.conn.commit()

            # Отправляем ответ пользователю, включая вопрос
            user_id = question[1]  # Предполагается, что user_id хранится во втором столбце таблицы
            question_text = question[3]  # Предполагается, что текст вопроса находится в четвертом столбце таблицы
            full_answer = f"Ответ на ваш вопрос '{question_text}':\n{answer_text}\n\nС уважением, команда ETALON MUSIC"
            bot.send_message(chat_id=user_id, text=full_answer)
            
            # Уведомляем о том, что ответ отправлен
            bot.reply_to(message, "Ответ на вопрос успешно отправлен.")
        else:
            bot.reply_to(message, "Вопрос с указанным номером не найден.")


    def close (self):
        self.conn.close()