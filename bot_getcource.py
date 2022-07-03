import json
import re
import time

import telebot
from telebot.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

import export_getcource_users_db
import in_out_db
from data import texts
import google_doc_api

with open('data/settings.json') as j:
    settings = json.load(j)
TOKEN = settings['token']
key_api = settings['key_api_getcource']
ID_GROUP_MENTORS = settings['id_group_mentors']
ID_GROUP_TECHSUPPORT = settings['id_group_techsupport']

telebot.apihelper.SESSION_TIME_TO_LIVE = 5 * 60
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
bot.delete_webhook()

dic_key_func = {
    '🟢 Вводная информация': 'intro_info',
    '➕ Тестирование': 'start_test',
    '🗨 Задать вопрос': 'question',
    '📢 Напоминания': 'reminder',
    '🕐 Уроки на неделю': 'questioning2',
    '⭕ Анкетирование': 'questioning'
}


def keyboard_menu():
    '''Клавиатура для главного меню, создается из ключей в dic_key_func'''
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*list(dic_key_func.keys()))
    return keyboard


def step_keyboard(text_list: list, row_width=2):
    '''Клавиатура для next_step, создается из текста в файле texts'''
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=row_width)
    keyboard.add(*text_list)
    return keyboard

# def step_keyboard(text_list):
#     keyboard = InlineKeyboardMarkup(row_width=2)
#     for num, text in enumerate(text_list):
#         btn = InlineKeyboardButton(text=text, callback_data = f'{text}:{num}')
#         keyboard.add(btn)
#     return keyboard


def url_buttons(array: dict):
    '''Берем словарь array и создаем URL кнопки'''
    markup = InlineKeyboardMarkup()
    for text_button, url in array.items():
        button = InlineKeyboardButton(text_button, url=url)
        markup.add(button)
    return markup


def validate_step_message(message, list_validate):
    '''Проверка корректности ввода в next_step'''
    if message.text in list_validate:
        print(message.text)
        return True


def validate_main_menu(message):
    '''Проверка корректности ввода в главном меню'''
    if message.text in dic_key_func.keys():
        return True


def send_start(message, text='Вернемся в основное меню'):
    '''Возврат в *главное* меню, добавляем кнопки *меню*'''
    telegram_id = message.from_user.id
    bot.send_message(telegram_id, text, reply_markup=keyboard_menu())


@bot.message_handler(commands=['start'])
def start(message):
    '''Точка входа'''
    telegram_id = message.from_user.id
    if not in_out_db.check_user_db(telegram_id):
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn_phone = KeyboardButton(text='📞 Передать номер телефона', request_contact=True)
        keyboard.row(btn_phone)
        bot.reply_to(message, texts.hello, reply_markup=keyboard)
    else:
        bot.send_message(telegram_id, 
                         f'''<b>Мы узнали тебя, {message.from_user.first_name}</b> 🙂''',
                         reply_markup=keyboard_menu())


@bot.message_handler(content_types=['contact'])
def get_phone(message):
    '''Первый вход. Запросим и получим номер телефона, сверим его в БД'''
    if message.contact is not None:
        telegram_id = message.contact.user_id
        phone = message.contact.phone_number.replace('+', '')
        if in_out_db.new_users_phone(telegram_id, phone):
            bot.send_message(telegram_id, 'Отлично! Ваш аккаунт telegram связан с аккаунтом getcource')
            questioning(message)
        elif not in_out_db.new_users_phone(telegram_id, phone):
            bot.send_message(telegram_id, 'Отправляем данные для проверки.... ')
            if export_getcource_users_db.update_users_info_db(False, telegram_id, phone):
                # извлечем данные о пользователе из API и добавим в БД
                msg = bot.send_message(telegram_id, 'Отлично! Ваш аккаунт telegram связан с аккаунтом getcource')
                bot.register_next_step_handler(msg, questioning)
            else:
                bot.send_message(telegram_id, f'Мы не смогли вас найти по номеру телефона {phone}, проверьте на странице профиля что номер привязанный к телеграм совпадает с номером привязанным к getcource https://courses.elenavolkova.school/user/my/profile. ')


@bot.message_handler(regexp='Анкетирование')
def questioning(message):
    telegram_id = message.from_user.id
    text = message.text
    if 'Назад' in text or text == '/start':
        send_start(message)
        return
    msg = bot.send_message(telegram_id, texts.choose_level, reply_markup=step_keyboard(texts.levels))
    bot.register_next_step_handler(msg, level_step)


def level_step(message):
    telegram_id = message.from_user.id
    text = message.text
    if 'Назад' in text or text == '/start':
        send_start(message)
        return
    if not validate_step_message(message, texts.levels):
        send_start(message, f'Не верно введены данные {text}, нажмите на кнопку для выбора')
        return
    bot.send_message(telegram_id, f'Выбран уровень: {text}')
    msg = bot.send_message(telegram_id, 'Укажите ваш возраст', reply_markup=step_keyboard(texts.age))
    bot.register_next_step_handler(msg, age_step)


def age_step(message):
    telegram_id = message.from_user.id
    text = message.text
    if 'Назад' in text:
        msg = bot.send_message(telegram_id, texts.choose_level, reply_markup=step_keyboard(texts.levels))
        bot.register_next_step_handler(msg, level_step)
    elif text == '/start':
        send_start(message)
        return
    elif not validate_step_message(message, texts.age):
        send_start(message, f'Не верно введены данные {text}, нажмите на кнопку для выбора')
        return
    else:
        bot.send_message(telegram_id, f'Выбран возраст: {text}')
        msg = bot.send_message(telegram_id, 'Какие проблемы вас беспокоят?', reply_markup=step_keyboard(texts.problems))
        bot.register_next_step_handler(msg, problems_step)


def problems_step(message):
    telegram_id = message.from_user.id
    text = message.text
    if 'Назад' in text:
        msg = bot.send_message(telegram_id, 'Укажите ваш возраст', reply_markup=step_keyboard(texts.age))
        bot.register_next_step_handler(msg, age_step)
    elif text == '/start':
        send_start(message)
        return
    elif not validate_step_message(message, texts.problems):
        send_start(message, f'Не верно введены данные {text}, нажмите на кнопку для выбора')
        return
    else:
        bot.send_message(telegram_id, f'Выбрана проблема: {text}')
        msg = bot.send_message(telegram_id, 'Сколько дней в неделю вы готовы заниматься, чтобы решить эти проблемы?', reply_markup=step_keyboard(texts.days_interval))
        bot.register_next_step_handler(msg, days_step)


def days_step(message):
    telegram_id = message.from_user.id
    text = message.text
    if 'Назад' in text:
        msg = bot.send_message(telegram_id, 'Какие проблемы вас беспокоят?', reply_markup=step_keyboard(texts.problems))
        bot.register_next_step_handler(msg, problems_step)
    elif text == '/start':
        send_start(message)
        return
    elif not validate_step_message(message, texts.days_interval):
        send_start(message, f'Не верно введены данные {text}, нажмите на кнопку для выбора')
        return
    else:
        bot.send_message(telegram_id, f'Периодичность занятий: {text}')
        msg = bot.send_message(telegram_id, 'Сколько времени в день вы готовы уделять?', reply_markup=step_keyboard(texts.time_inteval))
        bot.register_next_step_handler(msg, time_step)


def time_step(message):
    telegram_id = message.from_user.id
    text = message.text
    if 'Назад' in text:
        msg = bot.send_message(telegram_id, 'Сколько дней в неделю вы готовы заниматься, чтобы решить эти проблемы?', reply_markup=step_keyboard(texts.days_interval))
        bot.register_next_step_handler(msg, days_step)
    elif text == '/start':
        send_start(message)
        return
    elif not validate_step_message(message, texts.time_inteval):
        send_start(message, f'Не верно введены данные {text}, нажмите на кнопку для выбора')
        return
    else:
        bot.send_message(telegram_id, f'Выбрано время: {text}')
        msg = bot.send_message(telegram_id, texts.reminder_lesson,
                               reply_markup=step_keyboard(texts.cancel_reminder))
        bot.register_next_step_handler(msg, write_time_reminder, True)


def write_time_reminder(message, *step_triger):
    telegram_id = message.from_user.id
    text = message.text
    if 'Назад' in text and step_triger:
        msg = bot.send_message(telegram_id, 'Сколько времени в день вы готовы уделять?', reply_markup=step_keyboard(texts.time_inteval))
        bot.register_next_step_handler(msg, time_step)
    elif text == '/start' or 'Назад' in text:
        send_start(message)
        return
    elif text == texts.cancel_reminder[0]:
        in_out_db.update_one_variable_db(telegram_id, 'reminder_start_lessons', '')
        send_start(message,
                   '🟣 Мы не будем напоминавть о занятиях, вы всегда можете добавить напоминания нажав внизу кнопку <b>Напоминания</b>')
        return
    else:
        if not re.match(r'^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$', text):
            send_start(message, '🔴 Введите время правильно, в формате XX:XX Например 10:05 или 7:40')
            return
        elif in_out_db.update_one_variable_db(telegram_id, 'reminder_start_lessons', text):
            bot.send_message(telegram_id,
                             f'''🟢 Буду напоминать о занятиях в <b>{text}</b>. Вы можете изменить время напоминания нажав внизу кнопку <b>Напоминания</b>''')
            msg = bot.send_message(telegram_id, '''Выберите свой часовой пояс''',
                             reply_markup=step_keyboard([str(x) for x in range(-10, 11)], 5))
            if step_triger:
                bot.register_next_step_handler(msg, time_utc, True)
            else:
                bot.register_next_step_handler(msg, time_utc)
        else:
            bot.send_message(telegram_id, f'🔴 Не смог установить напоминание {text}, напишите в поддержку. Мы обязательно исправим проблему')


def time_utc(message, *step_triger):
    '''Запросим часовой пояс и добавим в БД'''
    telegram_id = message.from_user.id
    text = message.text
    send_start(message, f'🕒 Выбран часовой пояс: <b>{text}</b>')
    in_out_db.update_one_variable_db(telegram_id, 'utc', text)
    if step_triger:
        block_intro(message)


@bot.message_handler(regexp='Вводная информация', content_types=['text'])
def block_intro(message):
    '''Вызов функции Вводный блок из главного меню'''
    telegram_id = message.from_user.id
    bot.send_message(telegram_id,
                     'Ознакомьтесь с 5 базовыми лекциями о концепции движения',
                     reply_markup=url_buttons(texts.base_lections))
    time.sleep(2)
    bot.send_message(telegram_id,
                     'По кнопке <b>Вводная информация</b> всегда можно получить ссылки на 5 вводных лекций')


@bot.message_handler(regexp='Задать вопрос')
def ask_question(message):
    '''Задать вопрос и перенаправить его в чат менеджерам'''
    telegram_id = message.from_user.id
    msg = bot.send_message(telegram_id,
                           'Напишите свой вопрос для техподдержки (к сообщению можете прикрепить любое вложение (фото, видео и т.д)), мы ответим в этом чате')
    bot.register_next_step_handler(msg, forward_question)


def forward_question(message):
    '''Отправка вопроса в чат менеджерам'''
    text = message.text
    telegram_id = message.from_user.id

    if text in list(dic_key_func.keys()) or text == '/start':
        print(list(dic_key_func.keys()))
        return

    bot.forward_message(ID_GROUP_TECHSUPPORT, telegram_id, message.id)
    bot.send_message(telegram_id, '🌀 Благодарю за вопрос, мы вам скоро ответим....')


def match_chat_id(message):
    '''Проверка из какого чата слушать сообщения, для фильтрации'''
    if message.chat.id == ID_GROUP_TECHSUPPORT:
        return True


@bot.message_handler(func=match_chat_id, content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
def answer_mentor(message):
    '''Ответ ментора пользователю'''
    if message.chat.id == ID_GROUP_TECHSUPPORT and message.reply_to_message:
        bot.forward_message(message.json['reply_to_message']['forward_from']['id'], ID_GROUP_TECHSUPPORT, message.id)
        # bot.send_message(message.json['reply_to_message']['forward_from']['id'], f'Ответ ментора: {message.text}')


@bot.message_handler(regexp='Напоминания', content_types=['text'])
def main_write_time_reminder(message):
    '''Вызов функции Напоминаний из главного меню'''
    telegram_id = message.from_user.id
    time_remind = in_out_db.read_one_variable_db(telegram_id, 'reminder_start_lessons')
    if time_remind not in ('', None):
        bot.send_message(telegram_id, f'Текущее время напоминаний {time_remind}')
    if time_remind in ('', None):
        bot.send_message(telegram_id, 'Напоминаний о занятиях не установлено')
    msg = bot.send_message(telegram_id, texts.reminder_lesson_main_menu,
                           reply_markup=step_keyboard(texts.cancel_reminder))
    bot.register_next_step_handler(msg, write_time_reminder)


@bot.message_handler(regexp='Уроки на неделю')
def week_lessons(message):
    '''Вызов функции Подборка уроков на неделю из главного меню
    Парсим данные из gogole таблицы, получаем словарь в списке:
    ['неделя 1', {'урок 1': 'моб 1', 'урок 2': 'зст 1 - дыхание', 'урок 3': 'стаб 1', 'урок 4': 'моб 2'}]'''
    telegram_id = message.from_user.id
    level = in_out_db.read_one_variable_db(telegram_id, 'level')
    week = in_out_db.read_one_variable_db(telegram_id, 'week')
    lessons = google_doc_api.get_lessons_week(level, f'неделя {week}')
    if lessons:
        bot.send_message(telegram_id, f'<b>{lessons[0]}</b>',
                         reply_markup=url_buttons(lessons[1]))


@bot.message_handler(regexp='Тестирование')
def start_testing(message):
    '''Пройти тестирование, то есть отправить и получить видео от ментора'''
    telegram_id = message.from_user.id
    msg = bot.send_message(telegram_id, 'Выберите вариант для определения уровня вашей подготовки',
                           reply_markup=step_keyboard(['Cамостоятельно', 'C помощью ментора школы']))
    bot.register_next_step_handler(msg, step_testing)


def step_testing(message):
    telegram_id = message.from_user.id
    text = message.text
    if text == 'Cамостоятельно':
        msg = bot.send_message(telegram_id, texts.levels_descriptions,
                           reply_markup=step_keyboard(list(texts.dict_levels.keys())))
        bot.register_next_step_handler(msg, step_testing_self)
    elif text == 'C помощью ментора школы':
        img = open('data/pic/testing.png', 'rb')
        bot.send_photo(telegram_id, img)
        msg = bot.send_message(telegram_id, texts.levels_descriptions,
                           reply_markup=step_keyboard(['Приступить к тестированию', 'Назад']))
        bot.register_next_step_handler(msg, step_testing_mentor)


def step_testing_self(message):
    telegram_id = message.from_user.id
    text = message.text
    # if not validate_step_message(message, dict(texts.dict_levels.keys())):
    #     send_start(message, f'Не верно введены данные {text}, нажмите на кнопку для выбора')
    #     return
    send_start(message, texts.thanks_choose_level)
    in_out_db.update_one_variable_db(telegram_id, 'level', texts.dict_levels.get(text))
    return


def step_testing_mentor(message):
    telegram_id = message.from_user.id
    text = message.text
    if text in ('/start', 'Назад', 'Отмена тестирования'):
        send_start(message, '❌ Отмена, в любой момент вы можете повторить тестирование')
        return
    bot.send_message(telegram_id, 'Посмотрите видео с инструкцией', reply_markup=url_buttons(texts.watch_video_test))
    msg = bot.send_message(telegram_id, f'<b>📽 Снимите себя на видео и прикрепите сюда (+ рекомендация как снять)</b>', reply_markup=step_keyboard(texts.test_video))
    bot.register_next_step_handler(msg, send_video_mentor, 1)


def send_video_mentor(message, count):
    telegram_id = message.from_user.id
    text = message.text
    print('send_video_mentor', count)
    if text in ('Отмена тестирования', '/start'):
        send_start(message, '❌ Отмена, в любой момент вы можете повторить тестирование')
        return
    if text and 'Назад' in text:
        count -= 1
        if count < 1:
            count = 1
        msg = bot.send_message(telegram_id, f'Снимите себя на видео {count} и прикрепите сюда', reply_markup=step_keyboard(texts.test_video))
        bot.register_next_step_handler(msg, send_video_mentor, count)
    elif message.video:
        count += 1
        bot.forward_message(ID_GROUP_MENTORS, telegram_id, message.id)
        if count == 6:
            send_start(message, texts.end_testing)
            return
        msg = bot.send_message(telegram_id, f'<b>{texts.test_video_step.get(count)}</b>')
        bot.register_next_step_handler(msg, send_video_mentor, count)
    if text == 'Как прикрепить видео':
        count -= 1
        if count < 1:
            count = 1
        video = open('data/video/add_video.mp4', 'rb')
        bot.send_message(telegram_id, f'Тут будет текстовая инструкция как прикрепить видео для Android и IOS, ниже видео')
        msg = bot.send_video(telegram_id, video)
        bot.register_next_step_handler(msg, send_video_mentor, count)


# @bot.message_handler(content_types=['text'])
# def echo_main_menu(message):
#     text = message.text
#     print(message)
    # for menu, command in dic_key_func.items():
    #     if menu == text:
    #         print(menu, text)
    # if text == 'Анкетирование':
    #     questioning(message)


if __name__ == '__main__':
    try:
        bot.infinity_polling()
    except:
        pass
