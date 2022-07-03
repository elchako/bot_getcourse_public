import json

import gspread

with open('data/settings.json') as j:
    settings = json.load(j)

gc = gspread.service_account(filename='data/botgetcource-c07da90566f6.json') # Указываем путь к JSON google api
sh = gc.open_by_key(settings['google_sheet_api'])


def get_list_level(level):
    '''Получим значения всех ячеек и столбцов листа'''
    worksheet = sh.get_worksheet(level) # доступ к 1 листу (начальный уровень)
    result = worksheet.get_all_values()
    return result


def get_lessons_week(level, week):
    '''Запакуем все в словарь и поищем по уроки на неделю
    вернем словарь в списке, пример:
    ['неделя 1', {'урок 1': 'моб 1', 'урок 2': 'зст 1 - дыхание', 'урок 3': 'стаб 1', 'урок 4': 'моб 2'}]'''
    levels = get_list_level(level)
    if levels:
        week_lessons = []
        result = []
        result.append(week)
        dict_lesson = {}
        for lesson in levels[2:]:
            week_lessons = dict(zip(levels[1], lesson))
            for key, value in week_lessons.items():
                if key == week:
                    dict_lesson.setdefault(lesson[0], value)
        result.append(dict_lesson)
        return result


if __name__ == '__main__':
    print(get_lessons_week(1, 'неделя 1'))
