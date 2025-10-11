#!/usr/bin/env python3
"""
Простой скрипт для быстрого создания тестовых данных
"""

import os
import sys

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from create_test_data import main

if __name__ == "__main__":
    print("CollabHub - Генератор тестовых данных")
    print("Этот скрипт создаст:")
    print("- 8 пользователей (3 клиента + 5 фрилансеров)")
    print("- 8 проектов в разных статусах")
    print("- Отклики, отзывы, сообщения и комментарии")
    print("- Все с паролем: test123")
    print()
    
    response = input("Продолжить? (y/n): ")
    if response.lower() in ['y', 'yes', 'да', 'д']:
        main()
    else:
        print("Отменено.")
