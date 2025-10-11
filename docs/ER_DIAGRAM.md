# Диаграммы базы данных CollabHub

## ER-диаграмма (Entity-Relationship)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                USERS                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│ id (PK)          │ INTEGER PRIMARY KEY AUTOINCREMENT                            │
│ email            │ TEXT UNIQUE NOT NULL                                         │
│ password         │ TEXT NOT NULL                                                │
│ role             │ TEXT NOT NULL ('client' | 'freelancer')                      │
│ name             │ TEXT                                                         │
│ avatar           │ TEXT                                                         │
│ about_me         │ TEXT                                                         │
│ activity         │ TEXT                                                         │
│ skills           │ TEXT                                                         │
│ rating           │ REAL DEFAULT 0.0                                             │
│ completed_projects│ INTEGER DEFAULT 0                                           │
│ phone            │ TEXT                                                         │
│ telegram         │ TEXT                                                         │
│ created_at       │ DATETIME DEFAULT CURRENT_TIMESTAMP                           │
│ portfolio_files  │ TEXT (JSON)                                                  │
│ portfolio_links  │ TEXT                                                         │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 1:N
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                JOBS                                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│ id (PK)          │ INTEGER PRIMARY KEY AUTOINCREMENT                            │
│ title            │ TEXT NOT NULL                                                │
│ description      │ TEXT NOT NULL                                                │
│ deadline         │ TEXT NOT NULL                                                │
│ status           │ TEXT NOT NULL ('open' | 'in_progress' | 'done')              │
│ creator_email    │ TEXT NOT NULL (FK → Users.email)                             │
│ priority         │ TEXT DEFAULT 'medium' ('low' | 'medium' | 'high')            │
│ files            │ TEXT (JSON)                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 1:N
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            APPLICATIONS                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ id (PK)          │ INTEGER PRIMARY KEY AUTOINCREMENT                            │
│ job_id           │ INTEGER NOT NULL (FK → Jobs.id)                              │
│ freelancer_email │ TEXT NOT NULL (FK → Users.email)                             │
│ status           │ TEXT NOT NULL DEFAULT 'pending'                              │
│                  │ ('pending' | 'accepted' | 'rejected' | 'completed')          │
│ UNIQUE(job_id, freelancer_email)                                                │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 1:N
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              REVIEWS                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│ id (PK)          │ INTEGER PRIMARY KEY AUTOINCREMENT                            │
│ job_id           │ INTEGER NOT NULL (FK → Jobs.id)                              │
│ freelancer_email │ TEXT NOT NULL (FK → Users.email)                             │
│ client_email     │ TEXT NOT NULL (FK → Users.email)                             │
│ rating           │ INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5)         │
│ comment          │ TEXT                                                         │
│ created_at       │ DATETIME DEFAULT CURRENT_TIMESTAMP                           │
│ UNIQUE(job_id, freelancer_email, client_email)                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              MESSAGES                                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│ id (PK)          │ INTEGER PRIMARY KEY AUTOINCREMENT                            │
│ sender_email     │ TEXT NOT NULL (FK → Users.email)                             │
│ receiver_email   │ TEXT NOT NULL (FK → Users.email)                             │
│ job_id           │ INTEGER (FK → Jobs.id, NULL for direct messages)             │
│ message          │ TEXT NOT NULL                                                │
│ created_at       │ DATETIME DEFAULT CURRENT_TIMESTAMP                           │
│ is_read          │ BOOLEAN DEFAULT FALSE                                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                          PROJECT_COMMENTS                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│ id (PK)          │ INTEGER PRIMARY KEY AUTOINCREMENT                            │
│ job_id           │ INTEGER NOT NULL (FK → Jobs.id)                              │
│ user_email       │ TEXT NOT NULL (FK → Users.email)                             │
│ comment          │ TEXT NOT NULL                                                │
│ created_at       │ DATETIME DEFAULT CURRENT_TIMESTAMP                           │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Связи между таблицами:

### Основные связи:
1. **Users → Jobs** (1:N)
   - Один пользователь может создать много проектов
   - `Jobs.creator_email` → `Users.email`

2. **Users → Applications** (1:N)
   - Один фрилансер может откликнуться на много проектов
   - `Applications.freelancer_email` → `Users.email`

3. **Jobs → Applications** (1:N)
   - Один проект может иметь много откликов
   - `Applications.job_id` → `Jobs.id`

4. **Jobs → Reviews** (1:N)
   - Один проект может иметь много отзывов
   - `Reviews.job_id` → `Jobs.id`

5. **Users → Reviews** (1:N)
   - Один фрилансер может получить много отзывов
   - `Reviews.freelancer_email` → `Users.email`

6. **Users → Reviews** (1:N)
   - Один клиент может оставить много отзывов
   - `Reviews.client_email` → `Users.email`

7. **Users → Messages** (1:N)
   - Один пользователь может отправить много сообщений
   - `Messages.sender_email` → `Users.email`

8. **Users → Messages** (1:N)
   - Один пользователь может получить много сообщений
   - `Messages.receiver_email` → `Users.email`

9. **Jobs → Messages** (1:N)
   - Один проект может иметь много сообщений в чате
   - `Messages.job_id` → `Jobs.id` (может быть NULL)

10. **Jobs → ProjectComments** (1:N)
    - Один проект может иметь много комментариев
    - `ProjectComments.job_id` → `Jobs.id`

11. **Users → ProjectComments** (1:N)
    - Один пользователь может оставить много комментариев
    - `ProjectComments.user_email` → `Users.email`

## Типы пользователей и их роли:

### CLIENT (Заказчик):
- Создает проекты (Jobs)
- Принимает/отклоняет отклики (Applications)
- Оставляет отзывы (Reviews)
- Общается в чате (Messages)
- Комментирует проекты (ProjectComments)

### FREELANCER (Исполнитель):
- Откликается на проекты (Applications)
- Получает отзывы (Reviews)
- Общается в чате (Messages)
- Комментирует проекты (ProjectComments)

## Статусы и состояния:

### Статусы проектов (Jobs.status):
- `open` - Открыт для откликов
- `in_progress` - В работе (есть принятый фрилансер)
- `done` - Завершен

### Статусы откликов (Applications.status):
- `pending` - Ожидает рассмотрения
- `accepted` - Принят
- `rejected` - Отклонен
- `completed` - Завершен

### Приоритеты проектов (Jobs.priority):
- `low` - Низкий
- `medium` - Средний
- `high` - Высокий
