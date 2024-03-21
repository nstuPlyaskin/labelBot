import sqlite3
import os
import json
from telebot.apihelper import ApiTelegramException
from telebot import types

# Получаем абсолютный путь к файлу базы данных и вайтлисту
db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'support')
whitelist_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'whitelist.json')

class DB:
    #init db
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    # @BUG - кажется проверяется не uid а артист нейм или я хз
    def checkArtistExists(self, artist_nickname):
        self.cursor.execute("SELECT * FROM artistsTable WHERE artistNickName = ?", (artist_nickname,))
        return self.cursor.fetchone() is not None

#~~~# ADMIN PART #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
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
        
        print("\n\nADDED NEW QUESTION: \nUID:", uid, "\nNAME:", userName, "\nQUESTION:", userQuestion, "\nMEDIA:", userMedia, "\n")
        self.conn.commit()

        # Оповещение пользователей из whitelist.json о новом вопросе
        with open(whitelist_path, "r") as f:
            whitelist_data = json.load(f)
            allowed_users = whitelist_data.get("allowed_users", [])  # Получаем список разрешенных пользователей
            for user_id in allowed_users:
                try:
                    bot.send_message(chat_id=user_id, text="Появился новый вопрос в базе данных поддержки!")
                except ApiTelegramException as e:
                    print(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
                    # Можно сделать что-то еще, например, отправить себе уведомление о проблеме
                    pass

        return
    
    # show questions from users
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
                bot.send_photo(chat_id=message.chat.id, photo=usermedia, caption=f"Вопрос №{id} от пользователя: {username}\nВопрос: {question}\n\nОсталось вопросов в очереди: {total_questions - 1}\nВопрос был задан {date}\n\nДля ответа используйте /answer (номер вопроса) и текст ответа.\nПример: /answer 69 Здравствуйте, я ответил на ваш вопрос.")
            # Иначе отправляем текстовое сообщение
            else:
                bot.send_message(chat_id=message.chat.id, text=f"Вопрос №{id} от пользователя: {username}\nВопрос: {question}\n\nОсталось вопросов в очереди: {total_questions - 1}\nВопрос был задан {date}\n\nДля ответа используйте /answer (номер вопроса) и текст ответа.\nПример: /answer 69 Здравствуйте, я ответил на ваш вопрос.")
        else:
            bot.send_message(chat_id=message.chat.id, text="На данный момент вопросов нет.")

    # get answer to uesr question
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

    # show list of all users
    def showUsers(self, bot, message):
        # Выполняем запрос для извлечения уникальных пользователей
        self.cursor.execute("SELECT DISTINCT userName, uid FROM supportTable")
        users = self.cursor.fetchall()

        # Проверяем, есть ли пользователи в базе данных
        if users:
            # Множество для отслеживания уже выведенных пользователей
            displayed_users = set()
            
            # Формируем строку для каждого уникального пользователя
            user_list = ""
            for user in users:
                # Проверяем, был ли пользователь уже выведен
                if user not in displayed_users:
                    user_list += f"Username: {user[0]}, UID: {user[1]}\n"
                    displayed_users.add(user)  # Добавляем пользователя в множество уже выведенных
            # Отправляем список пользователей
            bot.send_message(chat_id=message.chat.id, text="Список уникальных пользователей:\n\n" + user_list)
        else:
            bot.send_message(chat_id=message.chat.id, text="В базе данных нет пользователей.")

    # send message to UID
    def sendMessage(self, bot, message):
        # Разбиваем сообщение на аргументы
        args = message.text.split(maxsplit=2)
        
        # Проверяем, правильно ли введена команда
        if len(args) < 3:
            bot.reply_to(message, "Вы должны указать UID пользователя и текст сообщения. Пример: /message 123456 Привет, как дела?")
            return
        
        # Извлекаем uid пользователя и текст сообщения
        uid = args[1]
        message_text = args[2]
        
        try:
            # Пытаемся отправить сообщение пользователю с указанным uid
            bot.send_message(chat_id=uid, text="У вас новое сообщение от поддержки ETALON MUSIC:\n\n" + message_text)
            bot.reply_to(message, "Сообщение успешно отправлено.")
        except ApiTelegramException as e:
            bot.reply_to(message, f"Не удалось отправить сообщение пользователю с UID {uid}. Пожалуйста, проверьте правильность UID и повторите попытку.")
            print(f"Failed to send message to user with UID {uid}: {e}")

#~~~# ARTIST PART #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    def addArtist(self, artist_data):
            try:
                # Формируем SQL-запрос для вставки данных в таблицу
                query = "INSERT INTO artistsTable (uid, artistNickName, artistRealName, artistSpotify, artistContacts) VALUES (?, ?, ?, ?, ?)"
                
                # Получаем значения из словаря artist_data
                values = (artist_data["uid"], artist_data["artistNickName"], artist_data["artistRealName"], artist_data["artistSpotify"], artist_data["artistContacts"])
                
                # Выполняем запрос
                self.cursor.execute(query, values)
                
                # Подтверждаем изменения в базе данных
                self.conn.commit()
                
                # Возвращаем True, если операция выполнена успешно
                return True
            except Exception as e:
                print("Ошибка при добавлении артиста:", e)
                return False
            finally:
                # Закрываем соединение с базой данных
                self.conn.close()

    def check_artist_exists(self, artist_nickname):
        # Выполняем запрос к базе данных, чтобы проверить существование артиста с указанным никнеймом
        self.cursor.execute("SELECT COUNT(*) FROM artistsTable WHERE artistNickName=?", (artist_nickname,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def close(self):
        self.conn.close()