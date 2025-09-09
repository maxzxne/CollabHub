# 🚀 Развертывание на Render

## 📋 Настройки для Render

### 1. Основные настройки
- **Source Code**: `maxzxne/CollabHub`
- **Name**: `CollabHub`
- **Language**: `Python 3`
- **Branch**: `main`
- **Region**: `Oregon (US West)`
- **Root Directory**: `backend`

### 2. Команды
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Переменные окружения
Добавьте в разделе Environment Variables:
- `PYTHONPATH` = `backend`
- `PORT` = `10000` (или оставьте пустым)

### 4. Дополнительные настройки
- **Health Check Path**: `/`
- **Auto-Deploy**: `On Commit` (включено)

## 🔧 Что нужно исправить в настройках Render

### ❌ Неправильно:
```
Start Command: gunicorn your_application.wsgi
```

### ✅ Правильно:
```
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### ❌ Неправильно:
```
Root Directory: (пусто)
```

### ✅ Правильно:
```
Root Directory: backend
```

## 📁 Структура файлов для Render

```
CollabHub/
├── backend/                 # ← Root Directory
│   ├── main.py             # ← Точка входа
│   ├── requirements.txt    # ← Зависимости
│   ├── database.py
│   ├── models.py
│   ├── templates/
│   ├── static/
│   ├── uploads/
│   ├── Procfile            # ← Для Heroku (опционально)
│   └── render.yaml         # ← Конфигурация Render
├── .gitignore
└── README.md
```

## 🚀 Пошаговая инструкция

### 1. Настройте Render
1. В поле **Root Directory** введите: `backend`
2. В поле **Start Command** введите: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. В поле **Build Command** оставьте: `pip install -r requirements.txt`

### 2. Добавьте переменные окружения
В разделе **Environment Variables**:
- `PYTHONPATH` = `backend`
- `PORT` = `10000`

### 3. Нажмите "Deploy Web Service"

## 🔍 Возможные проблемы и решения

### Проблема: "Module not found"
**Решение**: Убедитесь, что Root Directory установлен в `backend`

### Проблема: "Port already in use"
**Решение**: Используйте переменную `$PORT` в Start Command

### Проблема: "Database not found"
**Решение**: База данных создается автоматически при первом запуске

### Проблема: "Static files not found"
**Решение**: Убедитесь, что папка `static` находится в `backend/static`

## 📊 Мониторинг

После деплоя вы сможете:
- Просматривать логи в папке "Logs"
- Мониторить производительность
- Настраивать автодеплой
- Управлять переменными окружения

## 🔄 Обновление

После каждого push в GitHub:
1. Render автоматически обнаружит изменения
2. Запустит Build Command
3. Перезапустит приложение с новым кодом

## 💰 Стоимость

- **Free план**: $0/месяц (512 MB RAM, 0.1 CPU)
- **Starter план**: $7/месяц (512 MB RAM, 0.5 CPU)
- **Standard план**: $25/месяц (2 GB RAM, 1 CPU)

Для начала используйте Free план, при необходимости можно апгрейдить.

## 🎉 Готово!

После настройки и деплоя ваше приложение будет доступно по адресу:
`https://collabhub.onrender.com` (или ваш уникальный URL)
