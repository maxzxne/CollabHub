"""
WSGI файл для развертывания на Render
Создает экземпляр FastAPI приложения для продакшн сервера
"""
import os
import sys

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app

if __name__ == "__main__":
    import uvicorn
    # Получаем порт из переменной окружения или используем 10000 по умолчанию
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

