# Доступ к базе данных CollabHub

## Информация для подключения через DBeaver

### Основные параметры подключения:
- **Тип БД**: SQLite
- **Файл БД**: `backend/freelance.db`
- **Путь**: `C:\Projects\diplom_birja\backend\freelance.db`

### Настройки подключения в DBeaver:

1. **Создание нового подключения:**
   - Тип: SQLite
   - Путь к файлу: `C:\Projects\diplom_birja\backend\freelance.db`

2. **Дополнительные настройки:**
   - Кодировка: UTF-8
   - Режим: Read-Write

### Структура базы данных:

#### Таблица Users (Пользователи)
```sql
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'client' или 'freelancer'
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
    portfolio_files TEXT,  -- JSON строка
    portfolio_links TEXT   -- Ссылки через \n
);
```

#### Таблица Jobs (Проекты)
```sql
CREATE TABLE Jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    deadline TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'open', 'in_progress', 'done'
    creator_email TEXT NOT NULL,
    priority TEXT DEFAULT 'medium',  -- 'low', 'medium', 'high'
    files TEXT  -- JSON строка с путями к файлам
);
```

#### Таблица Applications (Отклики)
```sql
CREATE TABLE Applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    freelancer_email TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'accepted', 'rejected', 'completed'
    UNIQUE(job_id, freelancer_email)
);
```

#### Таблица Reviews (Отзывы)
```sql
CREATE TABLE Reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    freelancer_email TEXT NOT NULL,
    client_email TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, freelancer_email, client_email)
);
```

#### Таблица Messages (Сообщения)
```sql
CREATE TABLE Messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_email TEXT NOT NULL,
    receiver_email TEXT NOT NULL,
    job_id INTEGER,  -- NULL для обычных сообщений, ID проекта для проектных
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);
```

#### Таблица ProjectComments (Комментарии к проектам)
```sql
CREATE TABLE ProjectComments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    user_email TEXT NOT NULL,
    comment TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES Jobs (id)
);
```

### Полезные SQL запросы для анализа:

#### Пользователи и их статистика:
```sql
SELECT 
    email,
    name,
    role,
    rating,
    completed_projects,
    created_at
FROM Users 
ORDER BY rating DESC, completed_projects DESC;
```

#### Проекты с количеством откликов:
```sql
SELECT 
    j.id,
    j.title,
    j.status,
    j.priority,
    j.creator_email,
    COUNT(a.id) as applications_count
FROM Jobs j
LEFT JOIN Applications a ON j.id = a.job_id
GROUP BY j.id
ORDER BY j.id DESC;
```

#### Активные диалоги:
```sql
SELECT 
    sender_email,
    receiver_email,
    job_id,
    COUNT(*) as message_count,
    MAX(created_at) as last_message
FROM Messages 
GROUP BY sender_email, receiver_email, job_id
ORDER BY last_message DESC;
```

#### Статистика по отзывам:
```sql
SELECT 
    freelancer_email,
    AVG(rating) as avg_rating,
    COUNT(*) as reviews_count
FROM Reviews 
GROUP BY freelancer_email
ORDER BY avg_rating DESC;
```

### Важные замечания:

1. **Пароли хэшированы** с помощью bcrypt - не хранятся в открытом виде
2. **Файлы портфолио** хранятся в папке `backend/uploads/portfolio/`
3. **Аватарки** хранятся в папке `backend/uploads/avatars/`
4. **Файлы проектов** хранятся в папке `backend/uploads/projects/`
5. **JSON поля** (portfolio_files, files) содержат массивы путей к файлам

### Резервное копирование:
```bash
# Создание бэкапа
cp backend/freelance.db backup/freelance_$(date +%Y%m%d_%H%M%S).db

# Восстановление из бэкапа
cp backup/freelance_20241201_120000.db backend/freelance.db
```

### Очистка тестовых данных:
```sql
-- Осторожно! Удаляет все данные
DELETE FROM Messages;
DELETE FROM Reviews;
DELETE FROM Applications;
DELETE FROM ProjectComments;
DELETE FROM Jobs;
DELETE FROM Users;
```
