import telebot
import sqlite3
import os
from datetime import datetime

# Путь к базе данных
db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'support')

# Функция для проверки наличия пользователя в базе данных
def check_user_exists(uid):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM usersTable WHERE uid = ?''', (uid,))
    result = c.fetchone()[0]
    conn.close()
    return result > 0

# Функция для добавления нового пользователя в базу данных
def add_new_user(uid, userName):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        user_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('''INSERT INTO usersTable (uid, userName, userDate) VALUES (?, ?, ?)''', (uid, userName, user_date))
        conn.commit()
        conn.close()
        print(f"Пользователь '{userName}' с uid '{uid}' успешно зарегистрирован в системе от {user_date}.")
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")