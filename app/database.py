# Импорты для работы с базой данных
import sqlite3
import os

# Название файла базы данных
DB_NAME = "freelance.db"

def get_connection():
    """Создает подключение к базе данных SQLite"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Возвращает результаты как словари
    # Включаем поддержку внешних ключей в SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Инициализирует базу данных и создает все необходимые таблицы"""
    conn = get_connection()
    cursor = conn.cursor()
    # Включаем поддержку внешних ключей ПЕРЕД созданием таблиц
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Таблица пользователей
    # Удаляем старую таблицу для пересоздания с правильной структурой
    cursor.execute("DROP TABLE IF EXISTS Users")
    # Commit не нужен здесь, так как мы сразу создаем новую таблицу
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
    
    # Добавляем новые колонки, если их нет (для совместимости с существующими БД)
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
    
    # Таблица проектов/заданий
    # Удаляем старую таблицу если она существует без FOREIGN KEY
    cursor.execute("DROP TABLE IF EXISTS Jobs")
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
            FOREIGN KEY (creator_email) REFERENCES Users (email)
        )
    """)

    # Добавляем недостающие колонки в Jobs (для совместимости)
    try:
        cursor.execute("ALTER TABLE Jobs ADD COLUMN priority TEXT DEFAULT 'medium'")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE Jobs ADD COLUMN files TEXT")
    except sqlite3.OperationalError:
        pass
    
    # Таблица откликов фрилансеров на проекты
    cursor.execute("DROP TABLE IF EXISTS Applications")
    cursor.execute("""
        CREATE TABLE Applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            freelancer_email TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            UNIQUE(job_id, freelancer_email),
            FOREIGN KEY (job_id) REFERENCES Jobs (id),
            FOREIGN KEY (freelancer_email) REFERENCES Users (email)
        )
    """)
    
    # Таблица отзывов клиентов о фрилансерах
    cursor.execute("DROP TABLE IF EXISTS Reviews")
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
            FOREIGN KEY (job_id) REFERENCES Jobs (id),
            FOREIGN KEY (freelancer_email) REFERENCES Users (email),
            FOREIGN KEY (client_email) REFERENCES Users (email)
        )
    """)
    
    # Таблица сообщений в чате
    cursor.execute("DROP TABLE IF EXISTS Messages")
    cursor.execute("""
        CREATE TABLE Messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_email TEXT NOT NULL,
            receiver_email TEXT NOT NULL,
            job_id INTEGER,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (sender_email) REFERENCES Users (email),
            FOREIGN KEY (receiver_email) REFERENCES Users (email),
            FOREIGN KEY (job_id) REFERENCES Jobs (id)
        )
    """)
    
    # Таблица комментариев к проектам
    cursor.execute("DROP TABLE IF EXISTS ProjectComments")
    cursor.execute("""
        CREATE TABLE ProjectComments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            user_email TEXT NOT NULL,
            comment TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES Jobs (id),
            FOREIGN KEY (user_email) REFERENCES Users (email)
        )
    """)

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
