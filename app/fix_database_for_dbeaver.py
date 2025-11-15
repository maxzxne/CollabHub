#!/usr/bin/env python3
"""
Скрипт для пересоздания базы данных с правильными FOREIGN KEY для DBeaver
DBeaver читает FOREIGN KEY из базы данных, поэтому они должны быть явно определены
"""
import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

DB_NAME = "freelance.db"

def recreate_db_for_dbeaver():
    """Пересоздает базу данных с правильными FOREIGN KEY для DBeaver"""
    # Удаляем старую базу
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print("Старая база данных удалена")
    
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    print("Создание таблиц с FOREIGN KEY...")
    
    # 1. Users (базовая таблица, без FOREIGN KEY)
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
    print("✓ Users создана")
    
    # 2. Jobs (связь с Users)
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
    print("✓ Jobs создана (1 FK: creator_email → Users.email)")
    
    # 3. Applications (связи с Jobs и Users)
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
    print("✓ Applications создана (2 FK: job_id → Jobs.id, freelancer_email → Users.email)")
    
    # 4. Reviews (связи с Jobs и Users)
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
    print("✓ Reviews создана (3 FK: job_id → Jobs.id, freelancer_email → Users.email, client_email → Users.email)")
    
    # 5. Messages (связи с Users и Jobs)
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
    print("✓ Messages создана (3 FK: sender_email → Users.email, receiver_email → Users.email, job_id → Jobs.id)")
    
    # 6. ProjectComments (связи с Jobs и Users)
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
    print("✓ ProjectComments создана (2 FK: job_id → Jobs.id, user_email → Users.email)")
    
    conn.commit()
    
    # Проверяем все FOREIGN KEY
    print("\n" + "="*60)
    print("Проверка FOREIGN KEY для DBeaver:")
    print("="*60)
    
    tables = {
        'Jobs': 1,
        'Applications': 2,
        'Reviews': 3,
        'Messages': 3,
        'ProjectComments': 2
    }
    
    total_fk = 0
    for table, expected in tables.items():
        cursor.execute(f'PRAGMA foreign_key_list({table})')
        fks = cursor.fetchall()
        total_fk += len(fks)
        status = "✓" if len(fks) == expected else "✗"
        print(f"{status} {table}: {len(fks)}/{expected} связей")
        for fk in fks:
            print(f"    → {fk[3]} → {fk[2]}.{fk[4]}")
    
    print("="*60)
    print(f"Всего создано: {total_fk} связей (ожидалось: 11)")
    print("="*60)
    
    if total_fk == 11:
        print("\n✓ УСПЕХ! Все связи созданы правильно!")
        print("Теперь DBeaver должен отобразить все связи на ER-диаграмме.")
        print(f"\nБаза данных: {os.path.abspath(DB_NAME)}")
        print("Откройте её в DBeaver и создайте ER-диаграмму.")
    else:
        print(f"\n⚠ ВНИМАНИЕ: Создано {total_fk} из 11 связей")
    
    conn.close()

if __name__ == "__main__":
    print("Пересоздание базы данных с FOREIGN KEY для DBeaver...")
    print("Это удалит все существующие данные!")
    response = input("Продолжить? (y/n): ")
    if response.lower() in ['y', 'yes', 'да', 'д']:
        recreate_db_for_dbeaver()
    else:
        print("Отменено.")

