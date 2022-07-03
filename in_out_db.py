import sqlite3


def check_user_db(telegram_id):
    '''Проверим по telegram_id есть ли пользователь в базе users_db'''
    con = sqlite3.connect('data/getcource.db')
    cur = con.cursor()
    cur.execute(f"SELECT * FROM users_db WHERE telegram_id = '{telegram_id}'")
    if cur.fetchone():
        con.close()
        return True
    con.close()
    return False


def update_one_variable_db(telegram_id, row_db, variable):
    '''Запишем\обновим одну переменную для telegram_id в базе users_db'''
    con = sqlite3.connect('data/getcource.db')
    cur = con.cursor()
    cur.execute(f"UPDATE users_db SET {row_db}='{variable}' WHERE telegram_id={telegram_id}")
    con.commit()
    con.close()
    return True


def read_one_variable_db(telegram_id, row_db):
    '''Прочитаем одну переменную для telegram_id в базе users_db'''
    con = sqlite3.connect('data/getcource.db')
    cur = con.cursor()
    cur.execute(f"SELECT {row_db} FROM users_db WHERE telegram_id={telegram_id}")
    data = cur.fetchone()
    if data:
        con.close()
        return data[0]
    con.close()
    return False


def new_users_phone(telegram_id, phone):
    '''проверка телефона в таблице users_from_api (периодическая выгрузка данных из API) 
    для добавления, при регистрации'''
    con = sqlite3.connect('data/getcource.db')
    cur = con.cursor()
    cur.execute(f"SELECT * FROM users_from_api WHERE phone like '%{phone}'")
    data = cur.fetchone()
    # пример data (255424186, 'elchako@ya.ru', '79651875659', 'Артем', None)
    if data:
        # если телефон в таблице users_from_api добавим данные + telegram_id в users_db
        cur.execute(f"INSERT OR REPLACE INTO users_db (telegram_id, getcource_id, email, phone, name) VALUES ({telegram_id}, {data[0]}, '{data[1]}', '{phone}', '{data[3]}')")
        con.commit()
        con.close()
        return True
    con.close()
    return False


def new_users_email(telegram_id, email):
    '''проверка почты в БД для добавления, при регистрации'''
    con = sqlite3.connect('data/getcource.db')
    cur = con.cursor()
    cur.execute(f"SELECT * FROM users_from_api WHERE email = '{email}'")
    data = cur.fetchone()
    print(data)
    # пример data (255424186, 'elchako@ya.ru', '79651875659', 'Артем', None)
    if data:
        # если почта в таблице users_from_api добавим данные + telegram_id в users_db
        cur.execute(f"INSERT OR REPLACE INTO users_db (telegram_id, getcource_id, email, phone, name) VALUES ({telegram_id}, {data[0]}, '{email}', '{data[2]}', '{data[3]}')")
        con.commit()
        con.close()
        return True
    return False
