import sqlite3
import os

DB_NAME = "freelance.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
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
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Добавляем новые колонки, если их нет
    try:
        cursor.execute("ALTER TABLE Users ADD COLUMN about_me TEXT")
    except sqlite3.OperationalError:
        pass  # Колонка уже существует
    
    try:
        cursor.execute("ALTER TABLE Users ADD COLUMN activity TEXT")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE Users ADD COLUMN skills TEXT")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE Users ADD COLUMN rating REAL DEFAULT 0.0")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE Users ADD COLUMN completed_projects INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE Users ADD COLUMN phone TEXT")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE Users ADD COLUMN telegram TEXT")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE Users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE Users ADD COLUMN portfolio_files TEXT")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE Users ADD COLUMN portfolio_links TEXT")
    except sqlite3.OperationalError:
        pass
    
    # Таблица заданий
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            deadline TEXT NOT NULL,
            status TEXT NOT NULL,
            creator_email TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            files TEXT
        )
    """)

    # Добавляем недостающие колонки в Jobs
    try:
        cursor.execute("ALTER TABLE Jobs ADD COLUMN priority TEXT DEFAULT 'medium'")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE Jobs ADD COLUMN files TEXT")
    except sqlite3.OperationalError:
        pass
    
    # Таблица откликов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            freelancer_email TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            UNIQUE(job_id, freelancer_email)
        )
    """)
    
    # Таблица отзывов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            freelancer_email TEXT NOT NULL,
            client_email TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(job_id, freelancer_email, client_email)
        )
    """)
    
    # Таблица сообщений
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_email TEXT NOT NULL,
            receiver_email TEXT NOT NULL,
            job_id INTEGER,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE
        )
    """)

    conn.commit()
    conn.close()
