HTTP-сервер, реализующий функциональность календаря:
- создание событий с проверкой занятости всех участников;
- уведомление участников;
- хранение событий в JSON-файле.

Структура проекта:
```
calendar_bot/
├── calendar_bot.py       # Flask-приложение, эндпоинты
├── auth.py               # Генерация и проверка входа
├── models.py             # Классы событий и пользователей
├── notification.py       # Отправка уведомлений
├── storage.py            # Хранение событий (в памяти с сохранением в JSON)
├── test_calendar_bot.py  # Тесты
└── requirements.txt      # Зависимости
```

Запуск:
1. Установите зависимости: `pip install -r requirements.txt`
2. Запустите тесты: `pytest test_calendar_bot.py`

Ручная проверка:
1. Запустите: `python calendar_bot.py`
2. В командной строке использовать команды по типу:

- Создание пользователя:            `curl -X POST http://localhost:5000/register -H "Content-Type: application/json" -d "{\"username\":\"Алиса\",\"password\":\"123\"}"`

- Авторизация пользователя:         `curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d "{\"username\":\"Алиса\",\"password\":\"123\"}"`

- Создание события:                 `curl -X POST http://localhost:5000/create_event -H "Authorization: Bearer !!!ТОКЕН!!!" -H "Content-Type: application/json" -d "{\"participants_usernames\":[\"Боб\"],\"start\":\"2025-05-01T10:00:00\",\"end\":\"2025-05-01T11:00:00\",\"title\":\"Встреча\"}"`

- Получение собтиый пользователя:   `curl -X GET http://localhost:5000/events -H "Authorization: Bearer !!!ТОКЕН!!!"`