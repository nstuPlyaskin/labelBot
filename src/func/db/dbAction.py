import sqlite3
import os
import json
from telebot.apihelper import ApiTelegramException
from telebot import types
from func.shared.keyboard import get_main_keyboard

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
        
        
    def showReleaseByArtist(self, bot, uid, artist_name):
        try:
            with self.conn:
                self.cursor.execute("SELECT artistID FROM artistsTable WHERE uid=? AND artistNickName=?", (uid, artist_name))
                artist_id = self.cursor.fetchone()[0]
                self.cursor.execute("SELECT * FROM releasesTable WHERE artistID=?", (artist_id,))
                releases_info = self.cursor.fetchall()

            if releases_info:
                for release in releases_info:
                    # Определяем значение для поля "Статус модерации"
                    moderation_status = "На модерации" if release[14] == 0 else "Отправлен на дистрибуцию" if release[14] == 1 else "Отклонён"

                    # Проверяем наличие причины отклонения
                    reject_reason = release[15] if release[15] else None

                    release_details = {
                        "Название релиза": release[4],
                        "Исполнитель": artist_name,
                        "Feat.": release[3] if release[3] else "На данный момент нет данных",
                        "Дата релиза": release[5],
                        "Жанр": release[6],
                        "UPC": release[10] if release[10] else "На данный момент нет данных",
                        "ISRC": release[11] if release[11] else "На данный момент нет данных",
                        "Прослушивания": release[12] if release[12] else "На данный момент нет данных",
                        "Статус модерации": moderation_status,
                    }

                    # Добавляем причину отклонения, если она есть
                    if reject_reason:
                        release_details["Причина отклонения"] = reject_reason

                    # Формируем сообщение для отправки в чат
                    message = ""
                    for key, value in release_details.items():
                        message += f"{key} - {value}\n"
                    message += "\n"

                    keyboard = get_main_keyboard()
                    bot.send_message(uid, message, reply_markup=keyboard)
            else:
                bot.send_message(uid, f"У артиста {artist_name} пока нет релизов в базе данных.")
        except sqlite3.Error as e:
            print("Ошибка при получении информации о релизах артиста:", e)


    # /edit id field value
    def update_release_field(self, release_id, field_name, new_value):
        try:
            with self.conn:
                # Проверяем, существует ли указанное поле в таблице releasesTable
                self.cursor.execute(f"PRAGMA table_info(releasesTable)")
                fields = [row[1] for row in self.cursor.fetchall()]
                if field_name not in fields:
                    raise ValueError(f"Поле '{field_name}' не существует в таблице releasesTable.")

                # Обновляем значение указанного поля для указанного релиза
                self.cursor.execute(f"UPDATE releasesTable SET {field_name} = ? WHERE releaseID = ?", (new_value, release_id))
                self.conn.commit()
        except Exception as e:
            raise e



    # list of all releases
    def get_all_albums(self):
        try:
            with self.conn:
                self.cursor.execute("SELECT * FROM releasesTable")
                albums = self.cursor.fetchall()
            return albums
        except sqlite3.Error as e:
            print("Error while fetching all albums:", e)
            return None


    # /mod id accepted одобрение релиза
    # В метод approve_release из класса DB добавляем отправку уведомления администратору
    def approve_release(self, release_id, bot, is_approved=True):
        try:
            # Обновляем значение поля isModerated на 1 или 0 в зависимости от статуса одобрения релиза
            moderation_status = 1 if is_approved else 0
            self.cursor.execute("UPDATE releasesTable SET isModerated = ? WHERE releaseID = ?", (moderation_status, release_id))
            self.conn.commit()
            
            if is_approved:
                print(f"Релиз с ID {release_id} одобрен")
            else:
                bot.send_message(uid, "Уведомление пользователю о статусе модерации релиза успешно отправлено")

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
            notification = ""
            if is_approved:
                notification = f"Ваш релиз \"{release_name}\" одобрен"
            else:
                notification = f"Ваш релиз \"{release_name}\" отклонен"

            if uid:
                bot.send_message(uid, notification)
            else:
                print(f"Пользователь с artistID {artist_id} не найден для отправки уведомления")

            # Отправляем уведомление администратору о успешной отправке уведомления пользователю
            bot.send_message(uid, "Уведомление пользователю о статусе модерации релиза успешно отправлено")
        except Exception as e:
            print(f"Error while approving release: {e}")


    # /mod id reject reason
    def reject_release(self, release_id, bot, reason=None):
        try:
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
                if reason:
                    notification += f"\nПричина: {reason}"
                    
                    # Обновляем поле rejectReason и isModerated в базе данных
                    self.cursor.execute("UPDATE releasesTable SET rejectReason = ?, isModerated = -1 WHERE releaseID = ?", (reason, release_id))

                print(f"Релиз: '{release_name}' с ID: '{release_id}' отклонён по причине: '{reason}'")
                bot.send_message(uid, "Уведомление пользователю о статусе модерации релиза успешно отправлено")
                bot.send_message(uid, notification)
                
                # Обновляем флаг isModerated в базе данных на -1 после отклонения релиза
                self.conn.commit()
                
            else:
                print(f"Пользователь с artistID {artist_id} не найден для отправки уведомления")
                bot.send_message(uid, "Уведомление пользователю о статусе модерации релиза успешно отправлено")
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

    def get_uid_by_release_id(self, artist_id):
        """
        Получает uid пользователя по идентификатору артиста.
        """
        try:
            # Запрос для получения uid по artist_id из таблицы artistsTable
            # self.cursor.execute("SELECT artistNickName FROM artistsTable WHERE artistID = ?", (artist_id,))
            query = """
                SELECT artistsTable.uid 
                FROM releasesTable 
                JOIN artistsTable ON releasesTable.artistID = artistsTable.artistID 
                WHERE releasesTable.releaseID = ?
            """
            
            # Параметры запроса - artist_id
            parameters = (artist_id,)
            
            # Выполняем запрос с параметрами
            result = self.execute_query(query, parameters)

            # Предполагается, что результат запроса возвращается в виде кортежа или списка кортежей
            if result:
                return result[0][0]  # Первый столбец первой строки результата
            else:
                return None  # Если пользователь с указанным ID не найден
        except Exception as e:
            print(f"Ошибка при получении uid по идентификатору артиста: {e}")
            return None


    def get_field_value(self, release_id, field_name):
        """
        Получает значение поля для указанного релиза.
        """
        try:
            # Здесь должна быть логика выполнения запроса к вашей базе данных
            # Пример:
            query = f"SELECT {field_name} FROM releasesTable WHERE releaseID = ?"
            # Предполагается, что вы уже имеете метод для выполнения запросов в вашей базе данных
            result = self.execute_query(query, (release_id,))

            # Предполагается, что результат запроса возвращается в виде кортежа или списка кортежей
            if result:
                return result[0][0]  # Первый столбец первой строки результата
            else:
                return None  # Если релиз с указанным ID не найден
        except Exception as e:
            print(f"Ошибка при получении значения поля: {e}")
            return None
        
    def execute_query(self, query, parameters=None):
        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
            self.conn.commit()  # Фиксируем изменения
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error while executing query: {e}")
            return None
        

    def savePromoRelease(self, release_data):
        try:
            self.cursor.execute("""
                INSERT INTO releasesPromo (artistNickName, feat, releaseName, releaseType, releasePitch, releaseGenre, releaseUPC, releaseDescription, releaseMarketing, releaseLinkFiles, artistContacts, artistLinkPhoto)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                release_data["artistNickName"], release_data["feat"], release_data["releaseName"], release_data["releaseType"],
                release_data["releasePitch"], release_data["releaseGenre"], release_data["releaseUPC"],
                release_data["releaseDescription"], release_data["releaseMarketing"], release_data["releaseLinkFiles"],
                release_data["artistContacts"], release_data["artistLinkPhoto"]
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error occurred while saving promo release: {str(e)}")
            return False
        
    def get_releases_by_uid(self, uid):
        try:
            # Выполняем запрос к базе данных, чтобы получить список релизов для конкретного пользователя
            query = """
                SELECT releasesTable.releaseName
                FROM releasesTable
                INNER JOIN artistsTable ON releasesTable.artistID = artistsTable.artistID
                WHERE artistsTable.uid = ?
            """
            self.cursor.execute(query, (uid,))
            releases = self.cursor.fetchall()
            return releases
        except sqlite3.Error as e:
            print("Ошибка при получении релизов по uid:", e)
            return None
        

    # В классе DB добавим метод get_release_details_by_name
    def get_release_details_by_name(self, artistNickName, release_name):
        try:
            self.cursor.execute("""
                SELECT releasesTable.releaseName, releasesTable.releaseGenre, releasesTable.releaseUPC,
                    artistsTable.artistContacts, artistsTable.artistLinkPhoto
                FROM releasesTable
                INNER JOIN artistsTable ON releasesTable.artistID = artistsTable.artistID
                WHERE releasesTable.artistNickName = ? AND releasesTable.releaseName = ?
            """, (artistNickName, release_name))
            release_details = self.cursor.fetchone()
            
            # Проверяем, что release_details не равен None и содержит не менее 5 элементов
            if release_details and len(release_details) >= 5:
                return release_details
            else:
                return None
        except sqlite3.Error as e:
            print("Ошибка при получении данных о релизе по имени:", e)
            return None



    def close(self):
        self.conn.close()
