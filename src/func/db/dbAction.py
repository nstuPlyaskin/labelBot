import sqlite3
import os
import json
from telebot.apihelper import ApiTelegramException
from telebot import types

# Получаем абсолютный путь к файлу базы данных и вайтлисту
db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')
whitelist_path = os.path.join(os.path.dirname(__file__), '..','..', 'db', 'whitelist.json')

class DB:
    def __init__(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")

    def checkArtistExists(self, artist_nickname):
        self.cursor.execute("SELECT * FROM artistsTable WHERE artistNickName = ?", (artist_nickname,))
        return self.cursor.fetchone() is not None
    
    def checkUIDExists(self, uid):
        self.cursor.execute("SELECT * FROM artistsTable WHERE uid = ?", (uid,))
        return self.cursor.fetchone() is not None

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

    def showUsers(self, bot, message):
        try:
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
        except sqlite3.Error as e:
            print(f"Ошибка при получении списка пользователей: {e}")

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

    def showUnmoderatedReleases(self):
        # Выполнить запрос к базе данных для получения всех релизов с isModerated = 0
        self.cursor.execute("SELECT * FROM releasesTable WHERE isModerated = 0")
        unmoderated_releases = self.cursor.fetchall()
        return unmoderated_releases
    
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
        except sqlite3.Error as e:
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
    
    # show aritst list by user UID
    def artistList(self, uid):
        try:
            # Получаем список артистов для данного UID
            self.cursor.execute("SELECT artistNickName FROM artistsTable WHERE uid=?", (uid,))
            artist_list = [row[0] for row in self.cursor.fetchall()]
            return artist_list
        except sqlite3.Error as e:
            print("Ошибка при получении списка артистов:", e)
            return []
        finally:
            # Закрываем соединение с базой данных
            self.conn.close()

    # Добавляем метод для получения ID артиста по его никнейму
    def get_artist_id(self, artist_nickname):
        try:
            self.cursor.execute("SELECT artistID FROM artistsTable WHERE artistNickName=?", (artist_nickname,))
            artist_id = self.cursor.fetchone()
            return artist_id[0] if artist_id else None
        except sqlite3.Error as e:
            print("Ошибка при получении ID артиста:", e)
            return None
        
    # Сохраняем релиз в бд
    def saveRelease(self, user_data):
        try:
            # Выполняем запрос к базе данных для сохранения данных о релизе
            query = """
                INSERT INTO releasesTable (
                    artistID, artistNickName, feat, releaseName, releaseDate, releaseGenre, 
                    releaseTiming, releaseExplicit, releaseLyrics, releaseLinkFiles
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = tuple(user_data[key] for key in ['artistID', 'artistNickName', 'feat', 'releaseName', 'releaseDate', 
                                                    'releaseGenre', 'releaseTiming', 'releaseExplicit', 
                                                    'releaseLyrics', 'releaseLinkFiles'])
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка при сохранении данных о релизе:", e)
            return False
        finally:
            # Закрываем соединение с базой данных
            self.conn.close()

    def get_release_details(self, release_id):
        try:
            # Выполняем запрос к базе данных, чтобы получить детали релиза по его ID
            self.cursor.execute("""
                SELECT r.releaseID, r.artistID, r.artistNickName, r.feat, r.releaseName, r.releaseDate, 
                    r.releaseGenre, r.releaseTiming, r.releaseExplicit, r.releaseLyrics, r.releaseUPC, 
                    r.releaseISRC, r.releaseStreams, r.releaseLinkFiles, r.isModerated, a.uid, a.artistRealName, a.artistSpotify
                FROM releasesTable r
                LEFT JOIN artistsTable a ON r.artistID = a.artistID
                WHERE r.releaseID = ?
            """, (release_id,))
            
            result = self.cursor.fetchone()

            if result:
                release_details = {
                    "Название релиза": result[4],
                    "ID Релиза": result [0],
                    "Имя артиста": result[2],
                    "UID артиста": result[15],
                    "Артисты на фите": result[3],
                    "Жанр": result[6],
                    "Тайминг для коротких видео": result[7],
                    "Есть ли ненормативная лексика": result[8],
                    "Текст трека / треков": result[9],
                    "Ссылка на файлы (обложка, аудио)": result[13],
                    "Дата публикации": result[5],
                    "Ссылка на профиль Spotify": result[17]
                }
                return release_details
            else:
                print("Релиз с указанным ID не найден.")
                return None
        except Exception as e:
            print(f"Ошибка при получении деталей релиза по ID: {e}")
            return None



    def get_user_artists(self, user_id):
        query = "SELECT artistNickName FROM artistsTable WHERE uid = ?"
        self.cursor.execute(query, (user_id,))
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]
    
    def get_release_by_name(self, artistNickName, release_name):
        try:
            # Выполняем запрос к базе данных, чтобы получить релиз с указанным именем
            query = "SELECT * FROM releasesTable WHERE artistNickName = ? AND releaseName = ?"
            self.cursor.execute(query, (artistNickName, release_name))
            release = self.cursor.fetchone()
            return release
        except sqlite3.Error as e:
            print("Ошибка при получении релиза по имени:", e)
            return None
        
        
    def get_unmoderated_releases(self):
        try:
            # Выполняем запрос к базе данных для получения всех релизов, у которых isModerated = 0
            self.cursor.execute("SELECT * FROM releasesTable WHERE isModerated = 0")
            releases = self.cursor.fetchall()

            # Возвращаем список релизов в виде списка словарей, где ключи соответствуют именам столбцов
            return [{'releaseID': release[0],
                    'artistID': release[1],
                    'artistNickName': release[2],
                    'feat': release [3],
                    'releaseName': release [4],
                    'releaseDate': release[5],
                    'releaseGenre': release[6],
                    'releaseTiming': release[7],
                    'releaseExplicit': release[8],
                    'releaseLyrics': release[9],
                    'releaseUPC': release[10],
                    'releaseISRC': release[11],
                    'releaseStreams': release[12],
                    'releaseLinkFiles': [13],
                    'isModerated': release[14] } for release in releases]
        except Exception as e:
            print(f"Error while fetching unmoderated releases: {e}")
            return []  # Возвращаем пустой список в случае ошибки

        
    def get_artist_name_by_id(self, artist_id):
        try:
            # Выполняем запрос к базе данных, чтобы получить имя артиста по его ID
            self.cursor.execute("SELECT artistNickName FROM artistsTable WHERE artistID = ?", (artist_id,))
            result = self.cursor.fetchone()

            if result:
                return result[0]  # Возвращаем имя артиста из результата запроса
            else:
                return None  # Возвращаем None, если артист с указанным ID не найден
        except Exception as e:
            print(f"Error while fetching artist name by ID: {e}, 'artistid' {artist_id}")
            return None  # Возвращаем None в случае ошибки
        

    def get_user_id(self, uid):
        try:
            self.cursor.execute("SELECT user_id FROM releasesTable WHERE uid = ?", (uid,))
            row = self.cursor.fetchone()
            if row:
                return row[0]
            else:
                print(f"Пользователь с uid {uid} не найден")
                return None
        except Exception as e:
            print(f"Ошибка при получении user_id по uid: {e}")
            return None



    # /mod id accepted одобрение релиза
    # В метод approve_release из класса DB добавляем отправку уведомления администратору
    def approve_release(self, release_id, bot):
        try:
            # Обновляем значение поля isModerated на 1 для указанного релиза
            self.cursor.execute("UPDATE releasesTable SET isModerated = 1 WHERE releaseID = ?", (release_id,))
            self.conn.commit()
            print(f"Релиз с ID {release_id} одобрен")

            # Получаем artistID пользователя, который загрузил релиз
            self.cursor.execute("SELECT artistID FROM releasesTable WHERE releaseID = ?", (release_id,))
            artist_id = self.cursor.fetchone()[0]

            # Получаем uid пользователя из таблицы artistsTable по artistID
            self.cursor.execute("SELECT uid FROM artistsTable WHERE artistID = ?", (artist_id,))
            uid = self.cursor.fetchone()[0]

            # Получаем название релиза из таблицы releasesTable по releaseID
            self.cursor.execute("SELECT releaseName FROM releasesTable WHERE releaseID = ?", (release_id,))
            release_name = self.cursor.fetchone()[0]

            # Отправляем уведомление пользователю
            if uid:
                notification = f"Ваш релиз \"{release_name}\" одобрен"
                bot.send_message(uid, notification)
            else:
                print(f"Пользователь с artistID {artist_id} не найден для отправки уведомления")

            # Отправляем уведомление администратору о успешной отправке уведомления пользователю
            bot.send_message(uid, "Уведомление пользователю о статусе модерации релиза успешно отправлено")
        except Exception as e:
            print(f"Error while approving release: {e}")


    # /mod id reject отклонение релиза
    # В метод reject_release из класса DB добавляем отправку уведомления пользователю
    def reject_release(self, release_id, bot):
        try:
            self.cursor.execute("UPDATE releasesTable SET isModerated = 1 WHERE releaseID = ?", (release_id,))
            self.conn.commit()
        
            # Получаем artistID пользователя, который загрузил релиз
            self.cursor.execute("SELECT artistID FROM releasesTable WHERE releaseID = ?", (release_id,))
            artist_id = self.cursor.fetchone()[0]

            # Получаем uid пользователя из таблицы artistsTable по artistID
            self.cursor.execute("SELECT uid FROM artistsTable WHERE artistID = ?", (artist_id,))
            uid = self.cursor.fetchone()[0]

            # Получаем название релиза из таблицы releasesTable по releaseID
            self.cursor.execute("SELECT releaseName FROM releasesTable WHERE releaseID = ?", (release_id,))
            release_name = self.cursor.fetchone()[0]

            # Отправляем уведомление пользователю о том, что его релиз отклонён
            if uid:
                notification = f"Ваш релиз \"{release_name}\" отклонён"
                bot.send_message(uid, notification)
            else:
                print(f"Пользователь с artistID {artist_id} не найден для отправки уведомления")
        except Exception as e:
            print(f"Error while rejecting release: {e}")


    # проверить статус релиза, на модерации он или нет
    def check_moderation_status(self, release_id):
        try:
            self.cursor.execute("SELECT isModerated FROM releasesTable WHERE releaseID = ?", (release_id,))
            row = self.cursor.fetchone()
            if row:
                return row[0]
            else:
                print(f"Релиз с ID {release_id} не найден")
                return None
        except Exception as e:
            print(f"Ошибка при проверке статуса модерации релиза: {e}")
            return None


    def close(self):
        self.conn.close()
