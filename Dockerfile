# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app/ .

# Создаем папки для загрузок
RUN mkdir -p uploads/avatars uploads/projects uploads/portfolio

# Открываем порт
EXPOSE 10000

# Команда запуска
CMD ["python", "main.py"]
