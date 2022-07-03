import requests
import json
from bot_getcource import key_api
from datetime import datetime, timedelta

DELTA = 3
date_now = datetime.today().date()
date_delta = date_now - timedelta(days=DELTA)

url = f"https://itmschool.getcourse.ru/pl/api/account/exports/9848718?key={key_api}"
url_get_export_id = "https://itmschool.getcourse.ru/pl/api/account/users?key={key_api}&status=active&created_at[from]={date_delta}"

# response = requests.request("GET", url)

# fields = json.loads(response.text)['info']['fields']
# items = json.loads(response.text)['info']['items']

# for item in items:
#     d = dict(zip(fields, item))
#     if d['Эл. почта'] == 'gluxovaol@yandex.ru':
#         if d['Название'] == 'Видеокурс «Упругая сила» Доступ к курсу для самостоятельной практики на 1 год':
#             print(d)

def get_user_api_from_phone(phone):
	response = requests.request("GET", url_get_export_id)




if __name__ == '__main__':
	print(response.text)