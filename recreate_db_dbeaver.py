#!/usr/bin/env python3
"""
Скрипт для пересоздания базы данных с FOREIGN KEY для DBeaver
Запустите: python recreate_db_dbeaver.py
"""
import sqlite3
import os

DB_NAME = "freelance.db"
DB_NEW = "freelance_new.db"

# Переименовываем старую базу если существует
if os.path.exists(DB_NAME):
    try:
        if os.path.exists(DB_NEW):
            os.remove(DB_NEW)
        os.rename(DB_NAME, DB_NAME + ".backup")
        print("Старая база переименована в .backup")
    except Exception as e:
        print(f"Не удалось переименовать базу: {e}")
        print("Создаю новую базу с именем freelance_new.db")
        DB_NAME = DB_NEW

conn = sqlite3.connect(DB_NAME)
conn.execute("PRAGMA foreign_keys = ON")
c = conn.cursor()

print("Создание таблиц с FOREIGN KEY...")

# Users
c.execute("""
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

# Jobs
c.execute("""
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

# Applications
c.execute("""
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

# Reviews
c.execute("""
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

# Messages
c.execute("""
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

# ProjectComments
c.execute("""
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

# Проверка
print("\nПроверка FOREIGN KEY:")
tables = ['Jobs', 'Applications', 'Reviews', 'Messages', 'ProjectComments']
total = 0
for table in tables:
    c.execute(f'PRAGMA foreign_key_list({table})')
    fks = c.fetchall()
    total += len(fks)
    print(f"  {table}: {len(fks)} связей")
    for fk in fks:
        print(f"    - {fk[3]} -> {fk[2]}.{fk[4]}")

print(f"\nВсего: {total} связей (ожидалось: 11)")
if total == 11:
    print("SUCCESS! Все связи созданы. Теперь откройте базу в DBeaver.")
else:
    print(f"WARNING: Создано только {total} из 11 связей")

conn.close()
print(f"\nБаза данных: {os.path.abspath(DB_NAME)}")

