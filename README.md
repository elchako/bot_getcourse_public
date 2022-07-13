# bot_getcource_public

*Бот для онлайн школы на getcource.*

Помогает проходить тестирования, занятия и напоминает об их начале.

Взаимодейсвует с API getcource (при авторизации проверяем номер телефона пользователя и сверяем с API getcource).

База данных на SQlite.

Ссылки на уроки загружаются из google таблицы. Взаимодействие с google api через gspread


### Техзадание:

**вводная информация**

**пройти тестирование**

**задать вопрос**

**подборка уроков на неделю**

### Регистрация в чат-боте

1. на сайте нажал вступить в клуб 
    1. страница после успешной оплаты (вы в клубе! ссылка на чат-бота кликай и подключайся)
    2. на почту приходит дублируется информация - письмо с инструкцией по подключению к боту
    3. уникальность клиента привязнная к id клиента в телеграм

### Анкетирование

1. Вставить вопросы с анкеты геткурса
    - анкетирование
        
        **Ваш опыт в двигательных практиках***
        
        - [ ]  Начинающий (занимаюсь спортом редко / вообще не занимаюсь)
        - [ ]  Практикую регулярные физические нагрузки
        - [ ]  Продвинутый любитель (стаж регулярных тренировок более 2-х лет, глубоко интересуюсь темой фитнеса, биомеханикой и техникой упражнений)
        - [ ]  Профессиональный спортсмен(Фитнес-тренер, йога инструктор, специалист по движению Остеопат, мануальный терапевт, массажист)
        
        **Ваш возраст***
        
        меньше 25 лет25-35 лет35-45 лет 45-55 летстарше 55 лет
        
        **Какие проблемы вас беспокоят?***
        
        - [ ]  Хронический стресс, недостаток энергии
            - [ ]  Боли в спине и шее
            - [ ]  Неправильная осанка
            - [ ]  Недостатки фигуры
        
        **Другая проблема**
        
        **Сколько дней в неделю вы готовы заниматься, чтобы решить эти проблемы?***
        
        1 раз в неделю2-3 раза в неделю4 раза в неделю и чаще
        
        **Сколько времени в день вы готовы уделять?***
        
        до 20 минут20-40 минутболее 40 минут
        
2. Если анкета на геткурсе уже заполнена , то анкета используется с геткурс. 
    1. понять какие возможности есть синхронизации с гет-курсом анкеты (потому что там есть распределение по группам исходя из данных анкеты. Детали можно обсудить с Еленой)
3. Вопросы: 
    1. хотите чтобы мы вам напоминали о начале тренировок, если да то:
        1. во сколько вам будет удобно получать оповещения, во сколько занимаетесь?

### Вводный блок

1. после регистрации приходит серия вводных сообщений знакомств (в телеграм-бот)
    1. 5 базовых лекций о концепции движения, чтобы получить эффект ( видео ссылками на ютубе)
    2. последним сообщением: по кнопке вводная информация всегда можно вызвать ссылки на 5 вводных лекций
    3. сообщение: чтобы Я могла подобрать для вас правильный набор уроков, рекомендую пройти тестирование (картинка со скрином на кнопку пройти тестирование)
2. кнопка **вводная информация** - при нажатии выходит список ссылок на видео вводных лекций

### Тестирование

1. кнопка **пройти тестирование** (для определения уровня подготовки, от уровня зависит алгоритм присылаемых уроков):
    1. при нажатиии на кнопку выходит вопрос
        - [ ]  определить уровень самостоятельно
        - [ ]  определить уровень с помощью ментора школы
    2. при выборе варианта **“самостоятельно”** выходит следующий опрос
        - [ ]  новичок (текст описания новичка - вы практически не делали занятий, вы ведете малоподвижный образ жизни и т.д.)
        - [ ]  средний уровень (текст)
        - [ ]  профи (текст)
        
        при выборе любого варианта:
        
        - выходит благодарность - “спасибо за выбор уровня - все уроки, которые будут приходить - будут приходит в соответствии с выбранным уровнем” - до встречи на уроках
        - за клиентом в системе фиксируется его уровень (в базе данных - дата и уровень)
    3. при выборе варианта **“с помощью ментора”:** 
        1. текст описания тестирования с картинкой и две кнопки: приступить к тестированию/назад (к главному меню)
        2. при нажатии на: приступить к тестированию
            1. первым сообщением (текст-посмотрите видео с инструкцией и )
            2. второе сообщение: видео с тестированием (в первом Лена приветствует)
            3. третье сообщение: снимите себя на видео, после чего нажмите на кнопку загрузить видео.
            4. появляются 2 кнопки: загрузить видео/назад (либо картинкой с инструкцией, либо если есть возможность кнопка прямо вызывает меню прикрепить файл из галерии)
                1. при нажатии на загрузить видео: выбрать файл из галлереи
            5. после отправки видео цикл повторяется 5 раз (5 видео тестов)
            6. после 5го видео сообщение: благдарим за тестирование в течение 24 часов вы получете обратную связь с рекомендацией занятиям (индивидуальные рекомендации) + помощь в опредении уровня уроков
        3. видео тестирования с идентификатором клиента отправляются “отвественному за тестирование” (через телеграм-бота в эккаунт группы менторов) 
            1. при возможности поставить счетчик тестов, которые ушло в группу
        4. ментор смотрит видео тестов, записывает видеорекомендации и по кнопке отправляет их клиенту
        5. рекомендации приходят клиенту в бот и следом 
        6. запускается меню самостоятельного выбора уровня

### Подборка уроков на неделю

1. В понедельник приходит мотивашка на неделю и список уроков на эту неделю со ссылками
    1. список уроков берется из алгоритма базы данных уроков  Алгоритм уроков
        1. учитывается уровень подготовки (из тестирования)
        2. учитывается время оповещения (из анкетирования)
2. Список уроков - это набор ссылок с кратким описанием
    1. ссылка по такому типу: **урок №1
        1. понять - можно ли сделать так, что если у клиента стоит мобильное приложение геткурс - перебрасывало сразу туда
3. ежедневно приходит мотивашка (Витя, привет урок через 5 минут, список уроков по кнопке)
    1. всплывает кнопка: **подборка уроков**
    2. при нажатии на кнопку выходит подборка уроков на неделю
    3. мотивашка приходит согласно анкетированию
4. кнопка - **подборка уроков на неделю**
    1. кнопка остается в меню постоянных кнопок
    

### Оплата подписки клуба

1. За 3 дня до конца подписки приходит уведомление со ссылкой на оплату (данные оплаты на гет-курсе)
