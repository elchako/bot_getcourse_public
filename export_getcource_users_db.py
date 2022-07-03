# периодическая выгрузка пользователей в БД, запуск cron один раз в сутки
import json
import sqlite3
import time
import logging
import requests
from bot_getcource import key_api

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=f'logs/export.log',
    level=logging.ERROR,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
)
logger.addHandler(logging.StreamHandler())

SEC = 3  # повторить попытку запроса API через сек
NUM = 20  # количество повторов запросов в API

# выгрузим пользователей группы 'Клуб' (id=2293343)
url_get_export_id = f'https://itmschool.getcourse.ru/pl/api/account/groups/2293343/users?key={key_api}&status=active'


def export_users_getcource(url):
    '''Получаем export_id для дальнейшей выгрузки users'''
    export = requests.request('GET', url_get_export_id).json()
    if export['success']:
        export_id = export['info']['export_id']
        return export_id
    logger.error(f'Не удалось получить ключ для экспорта, {export}')
    return False


def get_users_from_export():
    '''По имеющемуся export_id запрашиваем данные о пользователях,
    если данные не готовы запускаем цикл ожидания while'''
    export_id = export_users_getcource(url_get_export_id)

    if export_id:
        url_export_users = f'https://itmschool.getcourse.ru/pl/api/account/exports/{export_id}?key={key_api}'
        users = requests.request('GET', url_export_users).json()
        time.sleep(5)

        if users['success']:
            return users['info']['items']
        else:
            count = 0
            while count < NUM:
                time.sleep(SEC)  # Время необходимое для формирования запроса на getcource
                print('Файл еще не создан')
                count += 1
                if requests.request('GET', url_export_users).json()['success']:
                    return requests.request('GET', url_export_users).json()['info']['items']
                    break
        logger.error(f'Не удалось получить данные пользователей, {users}')
        return False


def get_oneuser_from_export(phone):
    '''По имеющемуся export_id запрашиваем данные об одном пользователе,
    если данные не готовы запускаем цикл ожидания while'''
    export_id = export_users_getcource(url_get_export_id)
    url_export_users = f'https://itmschool.getcourse.ru/pl/api/account/exports/{export_id}?key={key_api}'

    if export_id:
        time.sleep(5)
        while not requests.request('GET', url_export_users).json()['success']:
            print('Файл еще не создан')
            time.sleep(SEC)  # Время необходимое для формирования запроса на getcource
            break

        users = requests.request('GET', url_export_users).json()
        fields = users['info']['fields']
        items = users['info']['items']
        # совместим два списка с словарь и найдем нужные данные по номеру телефона
        for item in items:
            d = dict(zip(fields, item))
            if d['Телефон'].replace('+', '') == phone.replace('+', ''):
                return item

        logger.error(f'Не удалось получить данные пользователе с номером {phone}')
        return False


def update_users_info_db(many, telegram_id='', phone=''):
    '''Добавим пользователя или обновим инфо о нем
    если many=True обновляем данные всех юзеров, False одного'''
    con = sqlite3.connect('data/getcource.db')
    cur = con.cursor()

    if many and get_users_from_export():
        users = get_users_from_export()
        for user in users:
            getcource_id = user[0]
            email = user[1]
            phone = user[7]
            name = user[5]
            print(getcource_id, email, phone)
            cur.execute(f"INSERT OR REPLACE INTO users_from_api (getcource_id, email, phone, name) VALUES ({getcource_id}, '{email}', '{phone}', '{name}')")
            con.commit()
            con.close()
    elif many is False and get_oneuser_from_export(phone):
        user = get_oneuser_from_export(phone)
        print(user)
        getcource_id = user[0]
        email = user[1]
        name = user[5]
        print(getcource_id, email, phone)
        cur.execute(f"INSERT OR REPLACE INTO users_db (telegram_id, getcource_id, email, phone, name) VALUES ({telegram_id}, {getcource_id}, '{email}', '{phone}', '{name}')")
        cur.execute(f"INSERT OR REPLACE INTO users_from_api (getcource_id, email, phone, name) VALUES ({getcource_id}, '{email}', '{phone}', '{name}')")
        con.commit()
        con.close()
    else:
        return False


if __name__ == '__main__':
    update_users_info_db(many=True)
