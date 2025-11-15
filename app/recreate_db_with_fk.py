#!/usr/bin/env python3
"""
Скрипт для пересоздания базы данных с правильными FOREIGN KEY
Запустите этот скрипт один раз для создания базы с правильными связями
"""
import sqlite3
import os
import sys

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection

def recreate_db_with_fk():
    """Пересоздает базу данных с правильными FOREIGN KEY"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Включаем FOREIGN KEY
    cursor.execute("PRAGMA foreign_keys = ON")
    
    print("Удаление старых таблиц...")
    # Удаляем таблицы в правильном порядке (с учетом зависимостей)
    cursor.execute("DROP TABLE IF EXISTS Messages")
    cursor.execute("DROP TABLE IF EXISTS Reviews")
    cursor.execute("DROP TABLE IF EXISTS Applications")
    cursor.execute("DROP TABLE IF EXISTS ProjectComments")
    cursor.execute("DROP TABLE IF EXISTS Jobs")
    cursor.execute("DROP TABLE IF EXISTS Users")
    
    print("Создание таблицы Users...")
    cursor.execute("""
        CREATE TABLE Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT,
            avatar TEXT,
            about_me TEXT,
            activity TEXT,
            skills TEXT,
            rating REAL DEFAULT 0.0,
            completed_projects INTEGER DEFAULT 0,
            phone TEXT,
            telegram TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            portfolio_files TEXT,
            portfolio_links TEXT
        )
    """)
    
    print("Создание таблицы Jobs с FOREIGN KEY...")
    cursor.execute("""
        CREATE TABLE Jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            deadline TEXT NOT NULL,
            status TEXT NOT NULL,
            creator_email TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            files TEXT,
            FOREIGN KEY (creator_email) REFERENCES Users(email)
        )
    """)
    
    print("Создание таблицы Applications с FOREIGN KEY...")
    cursor.execute("""
        CREATE TABLE Applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            freelancer_email TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            UNIQUE(job_id, freelancer_email),
            FOREIGN KEY (job_id) REFERENCES Jobs(id),
            FOREIGN KEY (freelancer_email) REFERENCES Users(email)
        )
    """)
    
    print("Создание таблицы Reviews с FOREIGN KEY...")
    cursor.execute("""
        CREATE TABLE Reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            freelancer_email TEXT NOT NULL,
            client_email TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(job_id, freelancer_email, client_email),
            FOREIGN KEY (job_id) REFERENCES Jobs(id),
            FOREIGN KEY (freelancer_email) REFERENCES Users(email),
            FOREIGN KEY (client_email) REFERENCES Users(email)
        )
    """)
    
    print("Создание таблицы Messages с FOREIGN KEY...")
    cursor.execute("""
        CREATE TABLE Messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_email TEXT NOT NULL,
            receiver_email TEXT NOT NULL,
            job_id INTEGER,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (sender_email) REFERENCES Users(email),
            FOREIGN KEY (receiver_email) REFERENCES Users(email),
            FOREIGN KEY (job_id) REFERENCES Jobs(id)
        )
    """)
    
    print("Создание таблицы ProjectComments с FOREIGN KEY...")
    cursor.execute("""
        CREATE TABLE ProjectComments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            user_email TEXT NOT NULL,
            comment TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES Jobs(id),
            FOREIGN KEY (user_email) REFERENCES Users(email)
        )
    """)
    
    conn.commit()
    
    # Проверяем FOREIGN KEY
    print("\n" + "="*50)
    print("Проверка FOREIGN KEY:")
    print("="*50)
    tables = ['Jobs', 'Applications', 'Reviews', 'Messages', 'ProjectComments']
    total_fk = 0
    for table in tables:
        cursor.execute(f'PRAGMA foreign_key_list({table})')
        fks = cursor.fetchall()
        total_fk += len(fks)
        if fks:
            print(f"\n{table}: {len(fks)} связей")
            for fk in fks:
                print(f"  ✓ {fk[3]} -> {fk[2]}.{fk[4]}")
        else:
            print(f"\n{table}: 0 связей (ОШИБКА!)")
    
    print("\n" + "="*50)
    print(f"Всего создано {total_fk} связей (FOREIGN KEY)")
    print("="*50)
    
    if total_fk >= 10:
        print("\n✓ База данных успешно пересоздана со всеми FOREIGN KEY!")
        print("Теперь все связи будут отображаться в ER-диаграмме.")
    else:
        print("\n⚠ ВНИМАНИЕ: Не все связи созданы. Ожидалось 10 связей.")
    
    conn.close()

if __name__ == "__main__":
    print("Пересоздание базы данных с FOREIGN KEY...")
    print("Это удалит все существующие данные!")
    response = input("Продолжить? (y/n): ")
    if response.lower() in ['y', 'yes', 'да', 'д']:
        recreate_db_with_fk()
    else:
        print("Отменено.")

