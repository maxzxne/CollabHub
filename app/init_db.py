#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных на Render
Используется для создания всех необходимых таблиц при первом запуске
"""
import os
import sys

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db

if __name__ == "__main__":
    print("Инициализация базы данных...")
    init_db()
    print("База данных успешно инициализирована!")
