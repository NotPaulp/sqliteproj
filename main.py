import re
import sqlite3

def create_db_connection(db_name='text.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        address TEXT,
        email TEXT NOT NULL UNIQUE
    )
    ''')
    return cursor, conn

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_name(name):
    return bool(re.match(r'^[A-Za-zА-Яа-я-]+$', name))


def email_exists(email, cursor):
    cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', (email,))
    return cursor.fetchone()[0] > 0


def add(name, surname, address, email, cursor, conn):
    if is_valid_name(name) and is_valid_name(surname) \
            and is_valid_email(email) and not email_exists(email, cursor):
        cursor.execute('INSERT INTO users (name, surname, address, email) VALUES (?, ?, ?, ?)',
                       (name, surname, address, email))
        conn.commit()
        return True, "Пользователь успешно добавлен."
    return False, "Ошибка: Проверьте корректность данных."


def update(name, surname, address, email, cursor, conn):
    if email_exists(email, cursor):
        update_fields = []
        if is_valid_name(name) and name:
            update_fields.append(f"name = '{name}'")
        if is_valid_name(surname) and surname:
            update_fields.append(f"surname = '{surname}'")
        if address:
            update_fields.append(f"address = '{address}'")

        if update_fields:
            update_query = ', '.join(update_fields)
            cursor.execute(f'UPDATE users SET {update_query} WHERE email = ?', (email,))
            conn.commit()
            return True, "Данные пользователя успешно обновлены."
        return False, "Ошибка: Укажите хотя бы одно поле для обновления."
    return False, "Ошибка: Пользователь с таким email не найден."


def delete(email, cursor, conn):
    if email_exists(email, cursor):
        cursor.execute('DELETE FROM users WHERE email = ?', (email,))
        conn.commit()
        return True, "Пользователь успешно удален."
    return False, "Ошибка: Пользователь с таким email не найден."


def get_user(email, cursor):
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    if user:
        return True, f"Пользователь найден: Имя: {user[1]}, Фамилия: {user[2]}, Адрес: {user[3]}, Email: {user[4]}"
    return False, "Ошибка: Пользователь с таким email не найден."

if __name__ == '__main__':
    cursor, conn = create_db_connection()
    action = None
    while action != 0:
        try:
            action = int(input(
                'Добавить пользователя - 1, Обновить данные пользователя - 2, Удалить пользователя - 3, Получить пользователя - 4, Выйти - 0: '))
            if action == 1:
                name = input("Введите имя пользователя: ")
                surname = input("Введите фамилию пользователя: ")
                address = input("Введите адрес пользователя (ENTER - пропустить): ")
                email = input("Введите email пользователя: ")
                success, message = add(name, surname, address, email, cursor, conn)
            elif action == 2:
                email = input("Введите email пользователя для обновления: ")
                name = input("Введите новое имя пользователя (ENTER - не обновлять): ")
                surname = input("Введите новую фамилию пользователя (ENTER - не обновлять): ")
                address = input("Введите новый адрес пользователя (ENTER - не обновлять): ")
                success, message = update(name, surname, address, email, cursor, conn)
            elif action == 3:
                email = input("Введите email пользователя, которого нужно удалить: ")
                success, message = delete(email, cursor, conn)
            elif action == 4:
                email = input("Введите email пользователя для получения данных: ")
                success, message = get_user(email, cursor)
            elif action == 0:
                success, message = True, "Выход из программы."
            else:
                success, message = False, "Неверный ввод, пожалуйста, попробуйте снова."
            print(message)
        except ValueError:
            success, message = False, "Неверный ввод, пожалуйста, попробуйте снова."
            print(message)
    conn.close()
