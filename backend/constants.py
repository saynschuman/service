# Коды ошибок при массовом создании пользователей:
# ---------------------
USERS_CREATE = 0  # Пользователи успешно созданы
PARSE_ERROR = 1  # Ошибка файла
ALREADY_CREATED = 2  # Пользователь уже создан
INVALID_DATA = 3  # Ошибка валидации данных
INVALID_TIME_INTERVAL = 4  # Ошибка итервала времени

# Коды ошибок при добавлении вопросов из файла:
# ---------------------
QUESTIONS_CREATE = 0  # Вопросы успешно созданы
TASK_ID_ERROR = 2  # Ошибка ID задания
DB_ERROR = 4  # Ошибка базы данных

# Коды ошибок при создании прохождения теста:
# ---------------------
EXCEEDED_NUMBER = 5  # Превышено колличество пробных попыток в задании

MONTHS = {
    "января": '01',
    "февраля": '02',
    "марта": '03',
    "апреля": '04',
    "мая": '05',
    "июня": '06',
    "июля": '07',
    "августа": '08',
    "сентября": '09',
    "октября": '10',
    "ноября": '11',
    "декабря": '12',
}
