
# Импорты для FastAPI и веб-функциональности
from fastapi import FastAPI, Request, Form, HTTPException, Depends, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Стандартные библиотеки Python
import sqlite3
import os
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import re
import json

# Импорты из локальных модулей
from database import init_db, get_connection
from models import (
    get_user_by_email,
    verify_password,
    get_jobs,
    create_job,
    get_job_by_id,
    apply_to_job,
    create_user,
    hash_password,
    update_user_profile,
    get_user_by_id,
    get_applications,
    get_applications_by_freelancer,
    get_applications_for_client,
    update_application_status,
    get_application_by_id,
    delete_job,
    has_user_applied_to_job,
    get_user_application_status,
    complete_job,
    create_review,
    get_reviews_for_freelancer,
    get_job_reviews,
    has_reviewed_job,
    create_message,
    get_messages_between_users,
    get_user_conversations,
    mark_messages_as_read,
    get_users_by_role,
    get_user_profile_by_email,
    create_project_comment,
    get_project_comments,
    can_user_comment_on_project,
    create_access_token,
    verify_token,
    get_all_users_with_filters,
    get_project_participants,
    get_unread_messages_count,
)

# Создание экземпляра FastAPI приложения
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Добавляем фильтр для JSON в шаблоны
def from_json(value):
    """Парсит JSON строку в объект Python"""
    import json
    try:
        return json.loads(value)
    except:
        return []

templates.env.filters["from_json"] = from_json

# Принудительное перенаправление на HTTPS (только в продакшене)
if os.getenv("RENDER"):
    app.add_middleware(HTTPSRedirectMiddleware)
    # Доверенные хосты для Render
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.onrender.com", "*.render.com"])

# Монтирование статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка папок для загрузки файлов
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Создаем подпапки для разных типов файлов
(UPLOAD_DIR / "avatars").mkdir(exist_ok=True)      # Аватарки пользователей
(UPLOAD_DIR / "projects").mkdir(exist_ok=True)     # Файлы проектов
(UPLOAD_DIR / "portfolio").mkdir(exist_ok=True)    # Файлы портфолио

# Монтируем папку загрузок как статическую для доступа через URL
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Инициализация базы данных
init_db()

# Проверяем и создаем тестовые данные при первом запуске
def check_and_create_test_data():
    """Проверяет наличие данных и создает тестовые данные при первом запуске"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Проверяем, есть ли пользователи в базе
    cursor.execute("SELECT COUNT(*) FROM Users")
    user_count = cursor.fetchone()[0]
    
    conn.close()
    
    # Если пользователей нет, создаем тестовые данные
    if user_count == 0:
        print("База данных пуста. Создаем тестовые данные...")
        create_test_data()
        print("Тестовые данные созданы успешно!")
    else:
        print(f"В базе данных уже есть {user_count} пользователей. Тестовые данные не создаются.")

def create_test_data():
    """Создает тестовые данные для демонстрации"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Тестовые пользователи
    users = [
        # Клиенты
        {
            'email': 'client1@test.com',
            'name': 'Александр Петров',
            'role': 'client',
            'about_me': 'Предприниматель, занимаюсь разработкой мобильных приложений. Ищу талантливых разработчиков для интересных проектов.',
            'activity': 'Мобильная разработка, Стартапы',
            'skills': 'Product Management, UI/UX Design',
            'phone': '+7 (999) 123-45-67',
            'telegram': '@alex_petrov'
        },
        {
            'email': 'client2@test.com',
            'name': 'Мария Сидорова',
            'role': 'client',
            'about_me': 'Маркетолог с опытом работы в IT. Нужны специалисты для создания лендингов и рекламных материалов.',
            'activity': 'Маркетинг, Реклама',
            'skills': 'Digital Marketing, Analytics',
            'phone': '+7 (999) 234-56-78',
            'telegram': '@maria_sidorova'
        },
        {
            'email': 'client3@test.com',
            'name': 'Дмитрий Козлов',
            'role': 'client',
            'about_me': 'Владелец интернет-магазина. Ищу разработчиков для создания и поддержки сайта.',
            'activity': 'E-commerce, Интернет-торговля',
            'skills': 'Business Development, Sales',
            'phone': '+7 (999) 345-67-89',
            'telegram': '@dmitry_kozlov'
        },
        
        # Фрилансеры
        {
            'email': 'freelancer1@test.com',
            'name': 'Анна Волкова',
            'role': 'freelancer',
            'about_me': 'Frontend разработчик с 5-летним опытом. Специализируюсь на React, Vue.js и современном CSS.',
            'activity': 'Frontend разработка',
            'skills': 'React, Vue.js, JavaScript, TypeScript, CSS, HTML',
            'phone': '+7 (999) 456-78-90',
            'telegram': '@anna_volkova',
            'rating': 4.8,
            'completed_projects': 15
        },
        {
            'email': 'freelancer2@test.com',
            'name': 'Игорь Морозов',
            'role': 'freelancer',
            'about_me': 'Backend разработчик на Python и Django. Опыт работы с базами данных и API.',
            'activity': 'Backend разработка',
            'skills': 'Python, Django, PostgreSQL, Redis, Docker',
            'phone': '+7 (999) 567-89-01',
            'telegram': '@igor_morozov',
            'rating': 4.6,
            'completed_projects': 12
        },
        {
            'email': 'freelancer3@test.com',
            'name': 'Елена Соколова',
            'role': 'freelancer',
            'about_me': 'UI/UX дизайнер с креативным подходом. Создаю современные и удобные интерфейсы.',
            'activity': 'UI/UX дизайн',
            'skills': 'Figma, Adobe XD, Photoshop, Illustrator, Prototyping',
            'phone': '+7 (999) 678-90-12',
            'telegram': '@elena_sokolova',
            'rating': 4.9,
            'completed_projects': 20
        },
        {
            'email': 'freelancer4@test.com',
            'name': 'Сергей Новиков',
            'role': 'freelancer',
            'about_me': 'Full-stack разработчик. Работаю с современными технологиями и фреймворками.',
            'activity': 'Full-stack разработка',
            'skills': 'Node.js, Express, MongoDB, React, Next.js',
            'phone': '+7 (999) 789-01-23',
            'telegram': '@sergey_novikov',
            'rating': 4.7,
            'completed_projects': 18
        },
        {
            'email': 'freelancer5@test.com',
            'name': 'Ольга Кузнецова',
            'role': 'freelancer',
            'about_me': 'Копирайтер и контент-менеджер. Создаю качественные тексты для сайтов и соцсетей.',
            'activity': 'Копирайтинг, Контент-маркетинг',
            'skills': 'Копирайтинг, SEO, SMM, Контент-планирование',
            'phone': '+7 (999) 890-12-34',
            'telegram': '@olga_kuznetsova',
            'rating': 4.5,
            'completed_projects': 25
        }
    ]
    
    # Создаем пользователей
    for user in users:
        hashed_password = hash_password("test123")
        cursor.execute("""
            INSERT INTO Users (email, password, role, name, about_me, activity, skills, phone, telegram, rating, completed_projects)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user['email'], hashed_password, user['role'], user['name'], user['about_me'],
            user['activity'], user['skills'], user['phone'], user['telegram'],
            user.get('rating'), user.get('completed_projects')
        ))
    
    # Получаем клиентов для создания проектов
    cursor.execute("SELECT email FROM Users WHERE role = 'client'")
    clients = [row[0] for row in cursor.fetchall()]
    
    # Тестовые проекты
    jobs = [
        {
            'title': 'Разработка мобильного приложения для доставки еды',
            'description': 'Нужно создать мобильное приложение для iOS и Android с функциями заказа еды, отслеживания доставки и оплаты. Приложение должно быть современным и удобным для пользователей.',
            'deadline': '15.02.2025',
            'priority': 'high',
            'status': 'open',
            'creator_email': clients[0],
            'files': '[]'
        },
        {
            'title': 'Создание лендинга для IT-компании',
            'description': 'Требуется создать современный лендинг для IT-компании с адаптивным дизайном, формой обратной связи и интеграцией с CRM системой.',
            'deadline': '28.01.2025',
            'priority': 'medium',
            'status': 'in_progress',
            'creator_email': clients[1],
            'files': '[]'
        },
        {
            'title': 'Дизайн интерфейса для банковского приложения',
            'description': 'Создание UI/UX дизайна для мобильного банковского приложения. Нужен современный, безопасный и интуитивно понятный интерфейс.',
            'deadline': '10.03.2025',
            'priority': 'high',
            'status': 'open',
            'creator_email': clients[0],
            'files': '[]'
        },
        {
            'title': 'Написание текстов для сайта интернет-магазина',
            'description': 'Требуется написать продающие тексты для главной страницы, карточек товаров и разделов сайта интернет-магазина электроники.',
            'deadline': '20.01.2025',
            'priority': 'low',
            'status': 'done',
            'creator_email': clients[2],
            'files': '[]'
        },
        {
            'title': 'Разработка API для системы управления складом',
            'description': 'Создание REST API для системы управления складом с функциями учета товаров, отчетности и интеграции с внешними системами.',
            'deadline': '05.02.2025',
            'priority': 'medium',
            'status': 'open',
            'creator_email': clients[1],
            'files': '[]'
        },
        {
            'title': 'Создание корпоративного сайта',
            'description': 'Разработка корпоративного сайта с админ-панелью для управления контентом, блогом и новостями компании.',
            'deadline': '15.03.2025',
            'priority': 'medium',
            'status': 'in_progress',
            'creator_email': clients[2],
            'files': '[]'
        },
        {
            'title': 'Дизайн логотипа и фирменного стиля',
            'description': 'Создание логотипа и разработка фирменного стиля для стартапа в сфере образовательных технологий.',
            'deadline': '25.01.2025',
            'priority': 'low',
            'status': 'done',
            'creator_email': clients[0],
            'files': '[]'
        },
        {
            'title': 'Интеграция платежной системы',
            'description': 'Интеграция различных платежных систем (Stripe, PayPal, Сбербанк) в существующее веб-приложение.',
            'deadline': '12.02.2025',
            'priority': 'high',
            'status': 'open',
            'creator_email': clients[1],
            'files': '[]'
        }
    ]
    
    # Создаем проекты
    for job in jobs:
        cursor.execute("""
            INSERT INTO Jobs (title, description, deadline, priority, status, creator_email, files)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            job['title'], job['description'], job['deadline'], job['priority'],
            job['status'], job['creator_email'], job['files']
        ))
    
    # Получаем фрилансеров для создания откликов
    cursor.execute("SELECT email FROM Users WHERE role = 'freelancer'")
    freelancers = [row[0] for row in cursor.fetchall()]
    
    # Создаем отклики
    applications = [
        {'job_id': 1, 'freelancer_email': freelancers[0], 'status': 'pending'},
        {'job_id': 1, 'freelancer_email': freelancers[3], 'status': 'pending'},
        {'job_id': 3, 'freelancer_email': freelancers[2], 'status': 'pending'},
        {'job_id': 3, 'freelancer_email': freelancers[0], 'status': 'pending'},
        {'job_id': 5, 'freelancer_email': freelancers[1], 'status': 'pending'},
        {'job_id': 5, 'freelancer_email': freelancers[3], 'status': 'pending'},
        {'job_id': 8, 'freelancer_email': freelancers[1], 'status': 'pending'},
        {'job_id': 8, 'freelancer_email': freelancers[3], 'status': 'pending'},
        {'job_id': 2, 'freelancer_email': freelancers[0], 'status': 'accepted'},
        {'job_id': 6, 'freelancer_email': freelancers[3], 'status': 'accepted'},
        {'job_id': 4, 'freelancer_email': freelancers[4], 'status': 'completed'},
        {'job_id': 7, 'freelancer_email': freelancers[2], 'status': 'completed'},
    ]
    
    for app in applications:
        cursor.execute("""
            INSERT INTO Applications (job_id, freelancer_email, status)
            VALUES (?, ?, ?)
        """, (app['job_id'], app['freelancer_email'], app['status']))
    
    # Создаем отзывы
    reviews = [
        {
            'job_id': 4,
            'freelancer_email': 'freelancer5@test.com',
            'client_email': 'client3@test.com',
            'rating': 5,
            'comment': 'Отличная работа! Тексты получились очень качественными и продающими. Рекомендую!'
        },
        {
            'job_id': 7,
            'freelancer_email': 'freelancer3@test.com',
            'client_email': 'client1@test.com',
            'rating': 5,
            'comment': 'Превосходный дизайн! Логотип и фирменный стиль получились именно такими, как я и представлял. Спасибо!'
        }
    ]
    
    for review in reviews:
        cursor.execute("""
            INSERT INTO Reviews (job_id, freelancer_email, client_email, rating, comment)
            VALUES (?, ?, ?, ?, ?)
        """, (
            review['job_id'], review['freelancer_email'], review['client_email'],
            review['rating'], review['comment']
        ))
    
    # Создаем сообщения
    messages = [
        {
            'sender_email': 'client2@test.com',
            'receiver_email': 'freelancer1@test.com',
            'job_id': 2,
            'message': 'Привет! Как дела с лендингом? Есть ли вопросы?',
            'created_at': datetime.now() - timedelta(hours=2)
        },
        {
            'sender_email': 'freelancer1@test.com',
            'receiver_email': 'client2@test.com',
            'job_id': 2,
            'message': 'Привет! Все хорошо, работаю над адаптивностью. Скоро покажу промежуточный результат.',
            'created_at': datetime.now() - timedelta(hours=1, minutes=30)
        },
        {
            'sender_email': 'client2@test.com',
            'receiver_email': 'freelancer1@test.com',
            'job_id': 2,
            'message': 'Отлично! Жду с нетерпением.',
            'created_at': datetime.now() - timedelta(hours=1)
        },
        {
            'sender_email': 'client3@test.com',
            'receiver_email': 'freelancer5@test.com',
            'job_id': 4,
            'message': 'Спасибо за отличную работу! Тексты получились очень качественными.',
            'created_at': datetime.now() - timedelta(days=1)
        },
        {
            'sender_email': 'freelancer5@test.com',
            'receiver_email': 'client3@test.com',
            'job_id': 4,
            'message': 'Пожалуйста! Рада была помочь. Если понадобятся еще тексты - обращайтесь!',
            'created_at': datetime.now() - timedelta(days=1, hours=-1)
        },
        {
            'sender_email': 'freelancer2@test.com',
            'receiver_email': 'freelancer3@test.com',
            'job_id': None,
            'message': 'Привет! Видела твои работы - очень круто! Может, поработаем вместе над проектом?',
            'created_at': datetime.now() - timedelta(hours=3)
        },
        {
            'sender_email': 'freelancer3@test.com',
            'receiver_email': 'freelancer2@test.com',
            'job_id': None,
            'message': 'Привет! Конечно, было бы здорово! У меня есть несколько интересных проектов.',
            'created_at': datetime.now() - timedelta(hours=2, minutes=45)
        }
    ]
    
    for msg in messages:
        cursor.execute("""
            INSERT INTO Messages (sender_email, receiver_email, job_id, message, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            msg['sender_email'], msg['receiver_email'], msg['job_id'],
            msg['message'], msg['created_at']
        ))
    
    # Создаем комментарии
    comments = [
        {
            'job_id': 1,
            'user_email': 'freelancer1@test.com',
            'comment': 'Интересный проект! У меня есть опыт разработки подобных приложений. Готов обсудить детали.',
            'created_at': datetime.now() - timedelta(hours=4)
        },
        {
            'job_id': 1,
            'user_email': 'freelancer3@test.com',
            'comment': 'Отличная идея! Могу помочь с дизайном интерфейса, если понадобится.',
            'created_at': datetime.now() - timedelta(hours=3, minutes=30)
        },
        {
            'job_id': 3,
            'user_email': 'freelancer2@test.com',
            'comment': 'Банковские приложения - это серьезно! Нужен опытный backend разработчик?',
            'created_at': datetime.now() - timedelta(hours=2)
        },
        {
            'job_id': 5,
            'user_email': 'freelancer4@test.com',
            'comment': 'API для склада - это мой профиль! Работал с подобными системами. Могу предложить оптимальное решение.',
            'created_at': datetime.now() - timedelta(hours=1, minutes=15)
        }
    ]
    
    for comment in comments:
        cursor.execute("""
            INSERT INTO ProjectComments (job_id, user_email, comment, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            comment['job_id'], comment['user_email'], comment['comment'], comment['created_at']
        ))
    
    conn.commit()
    conn.close()

# Проверяем и создаем тестовые данные при запуске
check_and_create_test_data()


# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С ФАЙЛАМИ =====

def save_uploaded_file(file: UploadFile, subfolder: str) -> str:
    """Сохраняет загруженный файл и возвращает путь к нему"""
    # Проверяем тип файла
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Неподдерживаемый тип файла")
    
    # Проверяем размер файла (максимум 10MB)
    content = file.file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="Файл слишком большой")
    
    # Генерируем уникальное имя файла
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_extension}"
    file_path = UPLOAD_DIR / subfolder / filename
    
    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    return f"/uploads/{subfolder}/{filename}"


def delete_file(file_path: str):
    """Удаляет файл с сервера"""
    if file_path and file_path.startswith("/uploads/"):
        actual_path = UPLOAD_DIR / file_path[9:]  # Убираем "/uploads/"
        if actual_path.exists():
            actual_path.unlink()


def validate_date(date_str: str) -> str:
    """Валидирует дату в формате YYYY-MM-DD (HTML5 date input)"""
    if not date_str or not date_str.strip():
        raise ValueError("Дата не может быть пустой")
    
    date_str = date_str.strip()
    
    try:
        # Парсим дату в формате YYYY-MM-DD
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Проверяем, что дата не в прошлом (с запасом в 1 день)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if date_obj < today:
            raise ValueError("Дата не может быть в прошлом")
        
        # Возвращаем дату в формате YYYY-MM-DD для сохранения в БД
        return date_str
        
    except ValueError as e:
        if "time data" in str(e):
            raise ValueError("Неверный формат даты")
        raise


def format_date_for_display(date_str: str) -> str:
    """Конвертирует дату из формата YYYY-MM-DD в DD.MM.YYYY для отображения"""
    if not date_str:
        return ""
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d.%m.%Y')
    except ValueError:
        # Если дата уже в формате DD.MM.YYYY, возвращаем как есть
        return date_str


# ===== ФУНКЦИИ АУТЕНТИФИКАЦИИ И АВТОРИЗАЦИИ =====

def get_current_user(request: Request):
    # Сначала проверяем JWT токен
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        email = verify_token(token)
        if email:
            user = get_user_by_email(email)
            if user:
                if isinstance(user, sqlite3.Row):
                    user = dict(user)
                if not user.get("avatar"):
                    user["avatar"] = "/static/defaultAvatar.jpg"
                
                # Парсим JSON поля
                if user.get("portfolio_files"):
                    try:
                        user["portfolio_files"] = json.loads(user["portfolio_files"])
                    except Exception as e:
                        user["portfolio_files"] = []
                else:
                    user["portfolio_files"] = []
                
                # Добавляем счетчик непрочитанных сообщений
                user["unread_messages_count"] = get_unread_messages_count(email)
                
                return user
    
    # Fallback на cookie для совместимости
    email = request.cookies.get("user_email")
    if not email:
        return None
    user = get_user_by_email(email)
    if user:
        # если это Row, конвертируем в dict
        if isinstance(user, sqlite3.Row):
            user = dict(user)
        if not user.get("avatar"):
            user["avatar"] = "/static/defaultAvatar.jpg"
        
        # Парсим JSON поля
        if user.get("portfolio_files"):
            try:
                user["portfolio_files"] = json.loads(user["portfolio_files"])
            except Exception as e:
                user["portfolio_files"] = []
        else:
            user["portfolio_files"] = []
        
        # Добавляем счетчик непрочитанных сообщений
        user["unread_messages_count"] = get_unread_messages_count(email)
        
        return user
    return None


# Функции-декораторы для проверки авторизации
def require_login(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=302, detail="Redirect", headers={"Location": "/login"})
    return user


def require_role(role: str):
    def role_checker(user: dict = Depends(require_login)):
        if user["role"] != role:
            raise HTTPException(status_code=403, detail="Нет доступа")
        return user
    return role_checker


# ===== МАРШРУТЫ АУТЕНТИФИКАЦИИ =====

@app.get("/login")
async def login_get(request: Request):
    # Перенаправляем на главную страницу с overlay
    return RedirectResponse(url="/", status_code=302)


@app.post("/login")
async def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    user = get_user_by_email(email)
    error = None
    if not user:
        error = "Пользователь не найден"
    else:
        # sqlite3.Row → dict
        if isinstance(user, sqlite3.Row):
            user = dict(user)
        if not verify_password(password, user["password"]):
            error = "Неверный пароль"

    if error:
        # Возвращаем главную страницу с ошибкой в overlay
        jobs = get_jobs()
        jobs = [dict(job) if isinstance(job, sqlite3.Row) else job for job in jobs]
        return templates.TemplateResponse("index.html", {
            "request": request,
            "jobs": jobs,
            "user": None,
            "login_error": error,
            "selected_status": None,
            "total_jobs_count": len(jobs)
        }, status_code=400)

    # Создаем JWT токен
    access_token = create_access_token(data={"sub": email})
    
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="user_email", value=email, httponly=True)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/register")
async def register_get(request: Request):
    # Перенаправляем на главную страницу с overlay
    return RedirectResponse(url="/", status_code=302)


@app.post("/register")
async def register_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
):
    existing = get_user_by_email(email)
    if existing:
        # Возвращаем главную страницу с ошибкой в overlay
        jobs = get_jobs()
        jobs = [dict(job) if isinstance(job, sqlite3.Row) else job for job in jobs]
        return templates.TemplateResponse("index.html", {
            "request": request,
            "jobs": jobs,
            "user": None,
            "register_error": "Email уже зарегистрирован",
            "selected_status": None,
            "total_jobs_count": len(jobs)
        }, status_code=400)

    hashed = hash_password(password)
    create_user(email=email, hashed_password=hashed, role=role, name=name, avatar=None)

    # Создаем JWT токен
    access_token = create_access_token(data={"sub": email})

    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="user_email", value=email, httponly=True)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user_email")
    response.delete_cookie("access_token")
    return response


# ===== ГЛАВНАЯ СТРАНИЦА И ПРОЕКТЫ =====

@app.get("/")
async def home(request: Request, status: str = None):
    # Получаем пользователя без обязательной авторизации
    user = get_current_user(request)
    jobs = get_jobs(status)
    # Конвертируем все Row в dict
    jobs = [dict(job) if isinstance(job, sqlite3.Row) else job for job in jobs]
    
    # Фильтруем проекты в зависимости от авторизации пользователя
    visible_jobs = []
    for job in jobs:
        # Проверяем, есть ли принятые отклики на этот проект
        applications = get_applications(job["id"])
        has_accepted = any(app["status"] == "accepted" for app in applications)
        
        if user:
            # Для авторизованных пользователей - обычная логика
            if (job["creator_email"] == user["email"] or 
                job["status"] in ["in_progress", "done"] or
                not has_accepted):
                visible_jobs.append(job)
            elif user["role"] == "freelancer":
                has_applied = has_user_applied_to_job(job["id"], user["email"])
                if has_applied:
                    visible_jobs.append(job)
        else:
            # Для неавторизованных пользователей показываем только открытые проекты
            if job["status"] == "open" and not has_accepted:
                visible_jobs.append(job)
    
    # Добавляем информацию об откликах для авторизованных пользователей
    for job in visible_jobs:
        job["applications"] = get_applications(job["id"])
        if user and user["role"] == "freelancer":
            job["has_applied"] = has_user_applied_to_job(job["id"], user["email"])
            job["application_status"] = get_user_application_status(job["id"], user["email"])
        
        # Форматируем дату для отображения
        job["deadline"] = format_date_for_display(job["deadline"])
        
        # Получаем имя создателя проекта
        creator = get_user_by_email(job["creator_email"])
        if creator and isinstance(creator, sqlite3.Row):
            creator = dict(creator)
        job["creator_name"] = creator.get("name") if creator else job["creator_email"]
        
        # Получаем участников проекта
        job["participants"] = get_project_participants(job["id"])
    
    # Получаем общее количество проектов в системе
    all_jobs = get_jobs()
    total_jobs_count = len(all_jobs)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "jobs": visible_jobs,
        "user": user,
        "selected_status": status,
        "total_jobs_count": total_jobs_count
    })


# ===== СОЗДАНИЕ И УПРАВЛЕНИЕ ПРОЕКТАМИ =====

@app.get("/jobs/create")
async def job_create_get(request: Request, user: dict = Depends(require_role("client"))):
    return templates.TemplateResponse("create_job.html", {"request": request, "user": user})


@app.post("/jobs/create")
async def job_create_post(request: Request, user: dict = Depends(require_role("client")),
                          title: str = Form(...),
                          description: str = Form(...),
                          deadline: str = Form(...),
                          priority: str = Form("medium"),
                          files: list[UploadFile] = File(None)):
    # Валидируем дату
    try:
        deadline = validate_date(deadline)
    except ValueError as e:
        return templates.TemplateResponse("create_job.html", {
            "request": request,
            "user": user,
            "error": str(e)
        }, status_code=400)
    
    # Сохраняем файлы проекта
    file_paths = []
    if files:
        for file in files:
            if file.filename:  # Проверяем, что файл был загружен
                try:
                    file_path = save_uploaded_file(file, "projects")
                    file_paths.append(file_path)
                except HTTPException as e:
                    return templates.TemplateResponse("create_job.html", {
                        "request": request,
                        "user": user,
                        "error": str(e.detail)
                    }, status_code=400)
    
    # Создаем проект с файлами
    create_job(title, description, deadline, user["email"], priority=priority, files=file_paths)
    return RedirectResponse(url="/", status_code=302)


# Детальная страница проекта
@app.get("/jobs/{job_id}")
async def job_detail(request: Request, job_id: int, user: dict = Depends(require_login)):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Конвертируем Row в dict
    if isinstance(job, sqlite3.Row):
        job = dict(job)
    
    # Получаем отклики на проект
    applications = get_applications(job_id)
    # Конвертируем все Row в dict
    applications = [dict(app) if isinstance(app, sqlite3.Row) else app for app in applications]
    
    # Добавляем информацию об отклике пользователя для фрилансеров
    if user["role"] == "freelancer":
        user["application_status"] = get_user_application_status(job_id, user["email"])
    
    # Парсим файлы проекта
    if job.get("files"):
        import json
        try:
            job["files"] = json.loads(job["files"])
        except:
            job["files"] = []
    
    # Получаем имя создателя проекта
    creator = get_user_by_email(job["creator_email"])
    if creator and isinstance(creator, sqlite3.Row):
        creator = dict(creator)
    job["creator_name"] = creator.get("name") if creator else job["creator_email"]
    
    # Получаем комментарии к проекту
    comments = get_project_comments(job_id)
    comments = [dict(comment) if isinstance(comment, sqlite3.Row) else comment for comment in comments]
    
    # Проверяем, может ли пользователь комментировать
    can_comment = can_user_comment_on_project(job_id, user["email"])
    
    # Получаем участников проекта
    participants = get_project_participants(job_id)
    
    # Форматируем дату для отображения
    job["deadline"] = format_date_for_display(job["deadline"])
    
    return templates.TemplateResponse("job_detail.html", {
        "request": request, 
        "job": job, 
        "user": user,
        "applications": applications,
        "comments": comments,
        "can_comment": can_comment,
        "participants": participants
    })


# Отклик на проект
@app.post("/jobs/{job_id}/apply")
async def apply_post(request: Request, job_id: int, user: dict = Depends(require_role("freelancer"))):
    # Получаем проект и проверяем его статус
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Конвертируем Row в dict
    if isinstance(job, sqlite3.Row):
        job = dict(job)
    
    # Проверяем, что проект открыт для откликов
    if job["status"] != "open":
        raise HTTPException(status_code=400, detail="На этот проект нельзя откликнуться")
    
    apply_to_job(job_id, user["email"])
    return RedirectResponse(url=f"/jobs/{job_id}", status_code=302)


# Редактирование проекта
@app.get("/jobs/{job_id}/edit")
async def edit_job_get(request: Request, job_id: int, user: dict = Depends(require_login)):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Конвертируем Row в dict
    if isinstance(job, sqlite3.Row):
        job = dict(job)
    
    # Проверяем, что пользователь - создатель проекта
    if job["creator_email"] != user["email"]:
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    # Конвертируем дату в формат YYYY-MM-DD для HTML5 date input
    if job["deadline"]:
        try:
            # Если дата в формате DD.MM.YYYY, конвертируем в YYYY-MM-DD
            if '.' in job["deadline"]:
                date_obj = datetime.strptime(job["deadline"], '%d.%m.%Y')
                job["deadline"] = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            # Если дата уже в правильном формате или невалидна, оставляем как есть
            pass
    
    return templates.TemplateResponse("edit_job.html", {
        "request": request,
        "user": user,
        "job": job
    })


@app.post("/jobs/{job_id}/edit")
async def edit_job_post(
    request: Request,
    job_id: int,
    user: dict = Depends(require_login),
    title: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(...),
    priority: str = Form("medium")
):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Конвертируем Row в dict
    if isinstance(job, sqlite3.Row):
        job = dict(job)
    
    # Проверяем, что пользователь - создатель проекта
    if job["creator_email"] != user["email"]:
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    # Валидируем дату
    try:
        deadline = validate_date(deadline)
    except ValueError as e:
        return templates.TemplateResponse("edit_job.html", {
            "request": request,
            "user": user,
            "job": job,
            "error": str(e)
        }, status_code=400)
    
    # Обновляем проект
    from models import update_job
    update_job(job_id, title, description, deadline, job["status"], priority)
    
    return RedirectResponse(url=f"/jobs/{job_id}", status_code=302)


# Удаление проекта
@app.get("/jobs/{job_id}/delete")
async def delete_job_get(request: Request, job_id: int, user: dict = Depends(require_login)):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Проверяем, что пользователь - создатель проекта
    if isinstance(job, sqlite3.Row):
        job = dict(job)
    
    if job["creator_email"] != user["email"]:
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    # Удаляем проект
    delete_job(job_id)
    
    return RedirectResponse(url="/", status_code=302)


# ===== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ =====

@app.get("/profile")
async def profile_get(request: Request, user: dict = Depends(require_login)):
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})


@app.post("/profile")
async def profile_post(
    request: Request,
    user: dict = Depends(require_login),
    name: str = Form(""),
    about_me: str = Form(""),
    activity: str = Form(""),
    skills: str = Form(""),
    phone: str = Form(""),
    telegram: str = Form(""),
    email: str = Form(""),
    portfolio_links: str = Form(""),
    portfolio_files: list[UploadFile] = File(None),
    avatar: UploadFile = File(None),
):
    # Проверяем, не занят ли новый email другим пользователем
    if email and email != user["email"]:
        existing_user = get_user_by_email(email)
        if existing_user:
            return templates.TemplateResponse("profile.html", {
                "request": request, 
                "user": user,
                "error": "Этот email уже используется другим пользователем"
            })
    
    # Обрабатываем загрузку аватарки
    avatar_path = None
    if avatar and avatar.filename:
        try:
            # Проверяем, что это изображение
            if not avatar.content_type.startswith('image/'):
                return templates.TemplateResponse("profile.html", {
                    "request": request, 
                    "user": user,
                    "error": "Аватарка должна быть изображением"
                })
            
            # Удаляем старую аватарку
            if user.get("avatar") and user["avatar"].startswith("/uploads/"):
                delete_file(user["avatar"])
            
            avatar_path = save_uploaded_file(avatar, "avatars")
        except HTTPException as e:
            return templates.TemplateResponse("profile.html", {
                "request": request, 
                "user": user,
                "error": str(e.detail)
            })
    
    # Обрабатываем файлы портфолио
    portfolio_file_paths = []
    if portfolio_files:
        for file in portfolio_files:
            if file.filename:  # Проверяем, что файл был загружен
                try:
                    file_path = save_uploaded_file(file, "portfolio")
                    portfolio_file_paths.append(file_path)
                except HTTPException as e:
                    return templates.TemplateResponse("profile.html", {
                        "request": request, 
                        "user": user,
                        "error": f"Ошибка загрузки файла портфолио: {str(e.detail)}"
                    })
    
    # Получаем существующие файлы портфолио и добавляем новые
    existing_files = user.get("portfolio_files", [])
    if isinstance(existing_files, str):
        try:
            existing_files = json.loads(existing_files)
        except:
            existing_files = []
    
    # Добавляем новые файлы к существующим
    all_files = existing_files + portfolio_file_paths
    
    # Обрабатываем ссылки портфолио
    existing_links = user.get("portfolio_links", "")
    if existing_links and portfolio_links:
        # Объединяем существующие и новые ссылки
        existing_links_list = [link.strip() for link in existing_links.split('\n') if link.strip()]
        new_links_list = [link.strip() for link in portfolio_links.split('\n') if link.strip()]
        # Убираем дубликаты
        all_links = list(dict.fromkeys(existing_links_list + new_links_list))
        portfolio_links_final = '\n'.join(all_links) if all_links else None
    elif portfolio_links:
        portfolio_links_final = portfolio_links
    else:
        portfolio_links_final = existing_links if existing_links else None
    
    # Обновляем профиль
    update_user_profile(
        user_id=user["id"],
        name=name if name else None,
        about_me=about_me if about_me else None,
        activity=activity if activity else None,
        skills=skills if skills else None,
        phone=phone if phone else None,
        telegram=telegram if telegram else None,
        email=email if email else None,
        avatar=avatar_path,
        portfolio_links=portfolio_links_final,
        portfolio_files=json.dumps(all_files) if all_files else None
    )
    
    # Получаем обновленные данные пользователя
    updated_user = get_user_by_id(user["id"])
    if updated_user and isinstance(updated_user, sqlite3.Row):
        updated_user = dict(updated_user)
    
    # Парсим JSON поля
    if updated_user.get("portfolio_files"):
        try:
            updated_user["portfolio_files"] = json.loads(updated_user["portfolio_files"])
        except Exception as e:
            updated_user["portfolio_files"] = []
    else:
        updated_user["portfolio_files"] = []
    
    return templates.TemplateResponse("profile.html", {
        "request": request, 
        "user": updated_user,
        "success": "Профиль успешно обновлен!"
    })


# ===== УПРАВЛЕНИЕ ОТКЛИКАМИ =====

@app.get("/applications")
async def applications_get(request: Request, user: dict = Depends(require_login)):
    if user["role"] == "freelancer":
        applications = get_applications_by_freelancer(user["email"])
        template = "applications_freelancer.html"
    else:
        applications = get_applications_for_client(user["email"])
        template = "applications_client.html"
    
    # Конвертируем все Row в dict
    applications = [dict(app) if isinstance(app, sqlite3.Row) else app for app in applications]
    
    return templates.TemplateResponse(template, {
        "request": request,
        "user": user,
        "applications": applications
    })


@app.post("/applications/{application_id}/accept")
async def accept_application(request: Request, application_id: int, user: dict = Depends(require_login)):
    application = get_application_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    # Конвертируем Row в dict
    if isinstance(application, sqlite3.Row):
        application = dict(application)
    
    # Проверяем, что пользователь - создатель проекта
    job = get_job_by_id(application["job_id"])
    if isinstance(job, sqlite3.Row):
        job = dict(job)
    
    if job["creator_email"] != user["email"]:
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    update_application_status(application_id, "accepted")
    return RedirectResponse(url="/applications", status_code=302)


@app.post("/applications/{application_id}/reject")
async def reject_application(request: Request, application_id: int, user: dict = Depends(require_login)):
    application = get_application_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    # Конвертируем Row в dict
    if isinstance(application, sqlite3.Row):
        application = dict(application)
    
    # Проверяем, что пользователь - создатель проекта
    job = get_job_by_id(application["job_id"])
    if isinstance(job, sqlite3.Row):
        job = dict(job)
    
    if job["creator_email"] != user["email"]:
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    update_application_status(application_id, "rejected")
    return RedirectResponse(url="/applications", status_code=302)


# Завершение проекта
@app.post("/jobs/{job_id}/complete")
async def complete_job_post(request: Request, job_id: int, user: dict = Depends(require_role("freelancer"))):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    if isinstance(job, sqlite3.Row):
        job = dict(job)
    
    # Проверяем, что фрилансер принят на проект
    application_status = get_user_application_status(job_id, user["email"])
    if application_status != "accepted":
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    complete_job(job_id, user["email"])
    return RedirectResponse(url=f"/jobs/{job_id}", status_code=302)


# ===== СИСТЕМА ОТЗЫВОВ =====

@app.get("/reviews")
async def reviews_get(request: Request, user: dict = Depends(require_login)):
    if user["role"] == "freelancer":
        reviews = get_reviews_for_freelancer(user["email"])
        reviews = [dict(review) if isinstance(review, sqlite3.Row) else review for review in reviews]
        template = "reviews_freelancer.html"
    else:
        # Для клиентов показываем проекты, которые можно оценить
        jobs = get_jobs("done")
        jobs = [dict(job) if isinstance(job, sqlite3.Row) else job for job in jobs]
        # Фильтруем только свои завершенные проекты
        my_jobs = [job for job in jobs if job["creator_email"] == user["email"]]
        
        # Добавляем информацию о том, оставлен ли отзыв для каждого проекта
        for job in my_jobs:
            # Получаем принятого фрилансера для проекта
            applications = get_applications(job["id"])
            accepted_freelancer = None
            for app in applications:
                if isinstance(app, sqlite3.Row):
                    app = dict(app)
                if app["status"] in ["accepted", "completed"]:
                    accepted_freelancer = app["freelancer_email"]
                    break
            
            if accepted_freelancer:
                job["has_review"] = has_reviewed_job(job["id"], user["email"], accepted_freelancer)
            else:
                job["has_review"] = False
        
        template = "reviews_client.html"
        reviews = my_jobs
    
    return templates.TemplateResponse(template, {
        "request": request,
        "user": user,
        "reviews": reviews
    })


@app.get("/jobs/{job_id}/review")
async def review_form_get(request: Request, job_id: int, user: dict = Depends(require_login)):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    if isinstance(job, sqlite3.Row):
        job = dict(job)
    
    # Проверяем, что пользователь - создатель проекта
    if job["creator_email"] != user["email"]:
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    # Получаем принятого фрилансера (может быть accepted или completed)
    applications = get_applications(job_id)
    accepted_freelancer = None
    for app in applications:
        if isinstance(app, sqlite3.Row):
            app = dict(app)
        if app["status"] in ["accepted", "completed"]:
            accepted_freelancer = app["freelancer_email"]
            break
    
    if not accepted_freelancer:
        raise HTTPException(status_code=400, detail="Нет принятого фрилансера")
    
    # Проверяем, не оставил ли уже отзыв
    if has_reviewed_job(job_id, user["email"], accepted_freelancer):
        return templates.TemplateResponse("review_form.html", {
            "request": request,
            "user": user,
            "job": job,
            "freelancer_email": accepted_freelancer,
            "already_reviewed": True
        })
    
    return templates.TemplateResponse("review_form.html", {
        "request": request,
        "user": user,
        "job": job,
        "freelancer_email": accepted_freelancer,
        "already_reviewed": False
    })


@app.post("/jobs/{job_id}/review")
async def review_form_post(
    request: Request, 
    job_id: int, 
    user: dict = Depends(require_login),
    rating: int = Form(...),
    comment: str = Form("")
):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    if isinstance(job, sqlite3.Row):
        job = dict(job)
    
    # Проверяем, что пользователь - создатель проекта
    if job["creator_email"] != user["email"]:
        raise HTTPException(status_code=403, detail="Нет доступа")
    
    # Получаем принятого фрилансера (может быть accepted или completed)
    applications = get_applications(job_id)
    accepted_freelancer = None
    for app in applications:
        if isinstance(app, sqlite3.Row):
            app = dict(app)
        if app["status"] in ["accepted", "completed"]:
            accepted_freelancer = app["freelancer_email"]
            break
    
    if not accepted_freelancer:
        raise HTTPException(status_code=400, detail="Нет принятого фрилансера")
    
    # Проверяем рейтинг
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Рейтинг должен быть от 1 до 5")
    
    create_review(job_id, accepted_freelancer, user["email"], rating, comment)
    
    # Статистика уже обновляется автоматически в функции create_review
    print(f"Review created and stats updated for freelancer: {accepted_freelancer}")
    
    return RedirectResponse(url="/reviews", status_code=302)


# ===== ТЕСТОВЫЕ И АДМИНИСТРАТИВНЫЕ ENDPOINTS =====

@app.get("/test")
async def test_endpoint():
    return {"message": "Server is working", "status": "ok"}

@app.get("/admin/update-stats")
async def update_all_stats():
    """Обновляет статистику всех фрилансеров (админская функция)"""
    from models import update_all_freelancer_stats
    update_all_freelancer_stats()
    return {"message": "Статистика всех фрилансеров обновлена", "status": "ok"}

# Удален тестовый WebSocket endpoint - больше не нужен

# ===== API ДЛЯ ЧАТА =====

@app.post("/api/messages/send")
async def send_message_api(
    request: Request,
    user: dict = Depends(require_login),
    receiver_email: str = Form(...),
    message: str = Form(...),
    job_id: int = Form(None)
):
    """API для отправки сообщения"""
    try:
        # Проверяем, что пользователь не пытается отправить сообщение самому себе
        if receiver_email == user["email"]:
            return {"status": "error", "message": "Нельзя отправить сообщение самому себе"}
        
        # Проверяем, что получатель существует
        receiver = get_user_by_email(receiver_email)
        if not receiver:
            return {"status": "error", "message": "Получатель не найден"}
        
        # Сохраняем сообщение в базу данных
        try:
            create_message(
                sender_email=user["email"],
                receiver_email=receiver_email,
                message=message,
                job_id=job_id
            )
            return {"status": "success", "message": "Сообщение отправлено"}
        except ValueError as e:
            return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/messages/{other_user_email}")
async def get_messages_api(
    request: Request,
    other_user_email: str,
    user: dict = Depends(require_login),
    job_id: int = None,
    last_message_id: int = 0
):
    """API для получения новых сообщений"""
    try:
        # Получаем параметры из query string
        job_id = request.query_params.get("job_id")
        if job_id:
            job_id = int(job_id)
        
        last_message_id = request.query_params.get("last_message_id", "0")
        last_message_id = int(last_message_id)
        
        # Получаем сообщения между пользователями
        messages = get_messages_between_users(user["email"], other_user_email, job_id)
        messages = [dict(msg) if isinstance(msg, sqlite3.Row) else msg for msg in messages]
        
        # Фильтруем только новые сообщения (с ID больше last_message_id)
        new_messages = [msg for msg in messages if msg["id"] > last_message_id]
        
        # Отмечаем сообщения как прочитанные
        if new_messages:
            mark_messages_as_read(user["email"], other_user_email, job_id)
        
        return {
            "status": "success",
            "messages": new_messages,
            "last_message_id": max([msg["id"] for msg in messages]) if messages else 0
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ===== СТРАНИЦЫ ЧАТА И СООБЩЕНИЙ =====

@app.get("/messages")
async def messages_get(request: Request, user: dict = Depends(require_login)):
    conversations = get_user_conversations(user["email"])
    conversations = [dict(conv) if isinstance(conv, sqlite3.Row) else conv for conv in conversations]
    
    # Обновляем счетчик непрочитанных сообщений
    user["unread_messages_count"] = get_unread_messages_count(user["email"])
    
    return templates.TemplateResponse("messages.html", {
        "request": request,
        "user": user,
        "conversations": conversations
    })


# Чат с конкретным пользователем
@app.get("/chat/{other_user_email}")
async def chat_get(request: Request, other_user_email: str, user: dict = Depends(require_login), job_id: int = None):
    # Получаем сообщения между пользователями
    messages = get_messages_between_users(user["email"], other_user_email, job_id)
    messages = [dict(msg) if isinstance(msg, sqlite3.Row) else msg for msg in messages]
    
    # Получаем информацию о собеседнике
    other_user = get_user_by_email(other_user_email)
    if other_user and isinstance(other_user, sqlite3.Row):
        other_user = dict(other_user)
    
    # Отмечаем сообщения как прочитанные
    mark_messages_as_read(user["email"], other_user_email, job_id)
    
    # Обновляем счетчик непрочитанных сообщений
    user["unread_messages_count"] = get_unread_messages_count(user["email"])
    
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "user": user,
        "other_user": other_user,
        "messages": messages,
        "job_id": job_id
    })


# Проектный чат
@app.get("/jobs/{job_id}/chat")
async def project_chat_get(request: Request, job_id: int, user: dict = Depends(require_login)):
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    if isinstance(job, sqlite3.Row):
        job = dict(job)
    
    # Определяем собеседника
    if user["email"] == job["creator_email"]:
        # Если пользователь - создатель проекта, находим принятого фрилансера
        applications = get_applications(job_id)
        other_user_email = None
        for app in applications:
            if isinstance(app, sqlite3.Row):
                app = dict(app)
            if app["status"] in ["accepted", "completed"]:
                other_user_email = app["freelancer_email"]
                break
    else:
        # Если пользователь - фрилансер, собеседник - создатель проекта
        other_user_email = job["creator_email"]
    
    if not other_user_email:
        raise HTTPException(status_code=400, detail="Нет собеседника для чата")
    
    # Получаем сообщения
    messages = get_messages_between_users(user["email"], other_user_email, job_id)
    messages = [dict(msg) if isinstance(msg, sqlite3.Row) else msg for msg in messages]
    
    # Получаем информацию о собеседнике
    other_user = get_user_by_email(other_user_email)
    if other_user and isinstance(other_user, sqlite3.Row):
        other_user = dict(other_user)
    
    # Отмечаем сообщения как прочитанные
    mark_messages_as_read(user["email"], other_user_email, job_id)
    
    # Обновляем счетчик непрочитанных сообщений
    user["unread_messages_count"] = get_unread_messages_count(user["email"])
    
    return templates.TemplateResponse("project_chat.html", {
        "request": request,
        "user": user,
        "other_user": other_user,
        "job": job,
        "messages": messages
    })


# ===== ПРОФИЛИ ПОЛЬЗОВАТЕЛЕЙ =====

@app.get("/profiles")
async def profiles_get(request: Request, user: dict = Depends(require_login), 
                      role: str = None, min_rating: str = None):
    # Получаем пользователей с фильтрацией
    users = get_all_users_with_filters(role, min_rating)
    users = [dict(u) if isinstance(u, sqlite3.Row) else u for u in users]
    
    return templates.TemplateResponse("profiles.html", {
        "request": request,
        "user": user,
        "users": users,
        "selected_role": role,
        "selected_min_rating": min_rating
    })


@app.get("/profile/{user_email}")
async def user_profile_get(request: Request, user_email: str, user: dict = Depends(require_login)):
    profile_user = get_user_profile_by_email(user_email)
    if not profile_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if isinstance(profile_user, sqlite3.Row):
        profile_user = dict(profile_user)
    
    # Парсим JSON поля
    if profile_user.get("portfolio_files"):
        try:
            profile_user["portfolio_files"] = json.loads(profile_user["portfolio_files"])
        except:
            profile_user["portfolio_files"] = []
    else:
        profile_user["portfolio_files"] = []
    
    # Обрабатываем ссылки портфолио
    if not profile_user.get("portfolio_links"):
        profile_user["portfolio_links"] = ""
    
    # Получаем отзывы для фрилансера
    reviews = []
    if profile_user["role"] == "freelancer":
        reviews = get_reviews_for_freelancer(user_email)
        reviews = [dict(r) if isinstance(r, sqlite3.Row) else r for r in reviews]
    
    return templates.TemplateResponse("user_profile.html", {
        "request": request,
        "user": user,
        "profile_user": profile_user,
        "reviews": reviews
    })


# ===== КОММЕНТАРИИ К ПРОЕКТАМ =====

@app.post("/jobs/{job_id}/comment")
async def add_project_comment(
    request: Request,
    job_id: int,
    user: dict = Depends(require_login),
    comment: str = Form(...)
):
    # Проверяем, может ли пользователь комментировать проект
    if not can_user_comment_on_project(job_id, user["email"]):
        raise HTTPException(status_code=403, detail="Нет доступа к комментированию")
    
    if not comment.strip():
        raise HTTPException(status_code=400, detail="Комментарий не может быть пустым")
    
    create_project_comment(job_id, user["email"], comment.strip())
    return RedirectResponse(url=f"/jobs/{job_id}", status_code=302)


# ===== AJAX ENDPOINTS ДЛЯ УПРАВЛЕНИЯ ПОРТФОЛИО =====

@app.post("/profile/remove-portfolio-file")
async def remove_portfolio_file(request: Request, user: dict = Depends(require_login)):
    data = await request.json()
    file_path = data.get("file_path")
    
    if not file_path:
        return {"success": False, "error": "Путь к файлу не указан"}
    
    # Получаем текущие файлы пользователя
    current_files = user.get("portfolio_files", [])
    if isinstance(current_files, str):
        try:
            current_files = json.loads(current_files)
        except:
            current_files = []
    
    # Удаляем файл из списка
    updated_files = [f for f in current_files if f != file_path]
    
    # Обновляем профиль
    update_user_profile(
        user_id=user["id"],
        portfolio_files=json.dumps(updated_files) if updated_files else None
    )
    
    # Обновляем данные пользователя в сессии
    user["portfolio_files"] = updated_files
    
    return {"success": True}


@app.post("/profile/remove-portfolio-link")
async def remove_portfolio_link(request: Request, user: dict = Depends(require_login)):
    data = await request.json()
    link_to_remove = data.get("link")
    
    if not link_to_remove:
        return {"success": False, "error": "Ссылка не указана"}
    
    # Получаем текущие ссылки пользователя
    current_links = user.get("portfolio_links", "")
    if current_links:
        links_list = [link.strip() for link in current_links.split('\n') if link.strip()]
        # Удаляем ссылку из списка
        updated_links = [link for link in links_list if link != link_to_remove]
        updated_links_str = '\n'.join(updated_links) if updated_links else None
    else:
        updated_links_str = None
    
    # Обновляем профиль
    update_user_profile(
        user_id=user["id"],
        portfolio_links=updated_links_str
    )
    
    # Обновляем данные пользователя в сессии
    user["portfolio_links"] = updated_links_str
    
    return {"success": True}


# ===== ОБРАБОТЧИКИ ОШИБОК =====

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Обработчик 404 ошибок"""
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error_code": 404,
        "message": "Страница не найдена"
    }, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Обработчик 500 ошибок"""
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error_code": 500,
        "message": "Внутренняя ошибка сервера"
    }, status_code=500)

@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    """Обработчик 403 ошибок"""
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error_code": 403,
        "message": "Доступ запрещен"
    }, status_code=403)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc):
    """Общий обработчик исключений"""
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error_code": 500,
        "message": "Произошла непредвиденная ошибка"
    }, status_code=500)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)