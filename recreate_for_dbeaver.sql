PRAGMA foreign_keys = ON;

-- Удаляем все таблицы
DROP TABLE IF EXISTS Messages;
DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS Applications;
DROP TABLE IF EXISTS ProjectComments;
DROP TABLE IF EXISTS Jobs;
DROP TABLE IF EXISTS Users;

-- Создаем таблицы с FOREIGN KEY

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
);

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
);

CREATE TABLE Applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    freelancer_email TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    UNIQUE(job_id, freelancer_email),
    FOREIGN KEY (job_id) REFERENCES Jobs(id),
    FOREIGN KEY (freelancer_email) REFERENCES Users(email)
);

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
);

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
);

CREATE TABLE ProjectComments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    user_email TEXT NOT NULL,
    comment TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES Jobs(id),
    FOREIGN KEY (user_email) REFERENCES Users(email)
);

