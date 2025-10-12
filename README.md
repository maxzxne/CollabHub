# CollabHub

Современная платформа для фриланса, где заказчики и исполнители находят друг друга.

## 🚀 Быстрый старт

### Локальный запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
cd app
uvicorn main:app --host 0.0.0.0 --port 10000
```

### Деплой на Render

Проект автоматически деплоится на Render при пуше в main ветку.

## 📁 Структура проекта

```
CollabHub/
├── app/                    # Основное приложение
│   ├── main.py            # FastAPI приложение (1716 строк)
│   ├── models.py          # Модели БД (727 строк)
│   ├── database.py        # Подключение к БД (168 строк)
│   ├── constants.py       # Константы приложения (90 строк)
│   ├── utils.py           # Утилиты (121 строка)
│   ├── templates/         # HTML шаблоны (20 файлов)
│   ├── static/            # Статические ресурсы
│   │   ├── css/           # Стили (main.css)
│   │   ├── js/            # JavaScript файлы
│   │   │   ├── main.js    # Основные функции
│   │   │   ├── auth.js    # Авторизация
│   │   │   └── forms.js   # Валидация форм
│   │   ├── images/        # Изображения
│   │   │   ├── logo.svg   # Логотип проекта
│   │   │   └── favicon.svg # Иконка сайта
│   │   └── icons/         # Иконки интерфейса
│   └── uploads/           # Загруженные файлы
├── tests/                 # Тесты
│   ├── conftest.py        # Конфигурация тестов
│   ├── test_auth.py       # Тесты авторизации
│   ├── test_models.py     # Тесты моделей
│   └── test_api.py        # Тесты API
├── requirements.txt       # Зависимости Python
├── render.yaml           # Конфигурация Render
├── Dockerfile            # Docker конфигурация
├── docker-compose.yml    # Docker Compose
└── README.md             # Этот файл
```

## 🎯 Основные функции

- **Авторизация и регистрация** - JWT токены, bcrypt хэширование
- **Создание и управление проектами** - для заказчиков
- **Отклики на проекты** - для исполнителей
- **Система сообщений** - polling каждые 3 секунды
- **Отзывы и рейтинги** - после завершения проектов
- **Профили пользователей** - с портфолио и контактами

## 🛠 Технологии

- **Backend**: FastAPI, SQLite, JWT
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Тестирование**: pytest, httpx
- **Деплой**: Docker (локально) и Render.com (для тестирования и демонстрации в сети)

## 🧪 Тестирование

Для запуска тестов:

```bash
# Установка зависимостей для тестирования
pip install pytest httpx

# Запуск тестов
pytest tests/

# Запуск конкретного теста
pytest tests/test_auth.py -v
```

## 📚 Документация

Подробная документация находится в папке [`docs/`](docs/):

- [Руководство по деплою](docs/DEPLOYMENT_GUIDE.md)
- [Тестовые данные](docs/TEST_DATA_GUIDE.md)
- [Диаграммы БД](docs/ER_DIAGRAM.md)
- [Вопросы для защиты](docs/DEFENSE_QUESTIONS.md)

## 🎮 Тестовые пользователи

**Пароль для всех: `test123`**

### Клиенты:
- `client1@test.com` - Александр Петров
- `client2@test.com` - Мария Сидорова
- `client3@test.com` - Дмитрий Козлов

### Фрилансеры:
- `freelancer1@test.com` - Анна Волкова (Frontend, 4.8★)
- `freelancer2@test.com` - Игорь Морозов (Backend, 4.6★)
- `freelancer3@test.com` - Елена Соколова (UI/UX, 4.9★)
- `freelancer4@test.com` - Сергей Новиков (Full-stack, 4.7★)
- `freelancer5@test.com` - Ольга Кузнецова (Копирайтинг, 4.5★)

## 📄 Лицензия

Этот проект создан для дипломной работы.
