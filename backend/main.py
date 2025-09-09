
from fastapi import FastAPI, Request, Form, HTTPException, Depends, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import re
import json
# Удален неиспользуемый импорт


from database import init_db
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
)

app = FastAPI()

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# Добавляем фильтр для JSON
def from_json(value):
    import json
    try:
        return json.loads(value)
    except:
        return []

templates.env.filters["from_json"] = from_json

app.mount("/static", StaticFiles(directory="static"), name="static")

# Создаем папку для загрузок
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Создаем подпапки
(UPLOAD_DIR / "avatars").mkdir(exist_ok=True)
(UPLOAD_DIR / "projects").mkdir(exist_ok=True)
(UPLOAD_DIR / "portfolio").mkdir(exist_ok=True)

# Монтируем папку загрузок как статическую
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

init_db()

# Удален WebSocket менеджер - теперь используем простое AJAX решение


# --- Вспомогательные функции для файлов ---
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
    """Валидирует дату в формате DD.MM.YYYY"""
    if not date_str or not date_str.strip():
        raise ValueError("Дата не может быть пустой")
    
    date_str = date_str.strip()
    
    # Проверяем формат даты (более гибкий)
    if not re.match(r'^\d{1,2}\.\d{1,2}\.\d{2,4}$', date_str):
        raise ValueError("Дата должна быть в формате ДД.ММ.ГГГГ (например: 25.12.2024)")
    
    try:
        parts = date_str.split('.')
        if len(parts) != 3:
            raise ValueError("Неверный формат даты")
            
        day, month, year = parts
        day = int(day)
        month = int(month)
        year = int(year)
        
        # Если год двухзначный, добавляем 20
        if year < 100:
            year += 2000
        
        # Проверяем ограничения
        if day < 1 or day > 31:
            raise ValueError("День должен быть от 1 до 31")
        if month < 1 or month > 12:
            raise ValueError("Месяц должен быть от 1 до 12")
        if year < 2020 or year > 2030:
            raise ValueError("Год должен быть от 2020 до 2030")
        
        # Проверяем корректность даты
        date_obj = datetime(year, month, day)
        
        # Проверяем, что дата не в прошлом (с запасом в 1 день)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if date_obj < today:
            raise ValueError("Дата не может быть в прошлом")
        
        # Возвращаем дату в правильном формате
        return f"{day:02d}.{month:02d}.{year}"
        
    except ValueError as e:
        if "invalid literal" in str(e) or "day is out of range" in str(e):
            raise ValueError("Некорректная дата")
        raise e


# --- Вспомогательная функция ---
def get_current_user(request: Request):
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
        
        return user
    return None


# --- Depends для авторизации ---
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


# --- Аутентификация ---
@app.get("/login")
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


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
        return templates.TemplateResponse("login.html", {"request": request, "error": error}, status_code=400)

    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="user_email", value=email, httponly=True)
    return response


@app.get("/register")
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


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
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "Email уже зарегистрирован"}, status_code=400
        )

    hashed = hash_password(password)
    create_user(email=email, hashed_password=hashed, role=role, name=name, avatar=None)

    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="user_email", value=email, httponly=True)
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("user_email")
    return response


# --- Главная ---
@app.get("/")
async def home(request: Request, user: dict = Depends(require_login), status: str = None):
    jobs = get_jobs(status)
    # Конвертируем все Row в dict
    jobs = [dict(job) if isinstance(job, sqlite3.Row) else job for job in jobs]
    
    # Фильтруем проекты: скрываем те, где уже есть принятый фрилансер
    visible_jobs = []
    for job in jobs:
        # Проверяем, есть ли принятые отклики на этот проект
        applications = get_applications(job["id"])
        has_accepted = any(app["status"] == "accepted" for app in applications)
        
        # Показываем проект если:
        # 1. Это проект текущего пользователя (всегда виден создателю) ИЛИ
        # 2. Проект в статусе "in_progress" или "done" (видны всем) ИЛИ
        # 3. Нет принятых фрилансеров (открытые проекты) ИЛИ
        # 4. Пользователь уже откликнулся на этот проект
        if (job["creator_email"] == user["email"] or 
            job["status"] in ["in_progress", "done"] or
            not has_accepted):
            visible_jobs.append(job)
        elif user["role"] == "freelancer":
            has_applied = has_user_applied_to_job(job["id"], user["email"])
            if has_applied:
                visible_jobs.append(job)
    
    # Добавляем информацию об откликах для всех пользователей
    for job in visible_jobs:
        job["applications"] = get_applications(job["id"])
        if user["role"] == "freelancer":
            job["has_applied"] = has_user_applied_to_job(job["id"], user["email"])
            job["application_status"] = get_user_application_status(job["id"], user["email"])
        
        # Получаем имя создателя проекта
        creator = get_user_by_email(job["creator_email"])
        if creator and isinstance(creator, sqlite3.Row):
            creator = dict(creator)
        job["creator_name"] = creator.get("name") if creator else job["creator_email"]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "jobs": visible_jobs,
        "user": user,
        "selected_status": status
    })


# --- Создание проекта ---
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


# --- Детальная страница проекта ---
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
    
    return templates.TemplateResponse("job_detail.html", {
        "request": request, 
        "job": job, 
        "user": user,
        "applications": applications
    })


# --- Откликнуться ---
@app.post("/jobs/{job_id}/apply")
async def apply_post(request: Request, job_id: int, user: dict = Depends(require_role("freelancer"))):
    apply_to_job(job_id, user["email"])
    return RedirectResponse(url=f"/jobs/{job_id}", status_code=302)


# --- Редактирование проекта ---
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


# --- Удаление проекта ---
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


# --- Профиль пользователя ---
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
        portfolio_links=portfolio_links if portfolio_links else None,
        portfolio_files=json.dumps(all_files) if all_files else None
    )
    
    # Получаем обновленные данные пользователя
    updated_user = get_user_by_id(user["id"])
    if updated_user and isinstance(updated_user, sqlite3.Row):
        updated_user = dict(updated_user)
    
    return templates.TemplateResponse("profile.html", {
        "request": request, 
        "user": updated_user,
        "success": "Профиль успешно обновлен!"
    })


# --- Управление откликами ---
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


# --- Завершение проекта ---
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


# --- Отзывы ---
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
    
    # Получаем принятого фрилансера
    applications = get_applications(job_id)
    accepted_freelancer = None
    for app in applications:
        if isinstance(app, sqlite3.Row):
            app = dict(app)
        if app["status"] == "accepted":
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
    
    # Получаем принятого фрилансера
    applications = get_applications(job_id)
    accepted_freelancer = None
    for app in applications:
        if isinstance(app, sqlite3.Row):
            app = dict(app)
        if app["status"] == "accepted":
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


# --- Тестовые endpoints ---
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

# --- API для чата (простое решение без WebSocket) ---
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
        # Сохраняем сообщение в базу данных
        create_message(
            sender_email=user["email"],
            receiver_email=receiver_email,
            message=message,
            job_id=job_id
        )
        return {"status": "success", "message": "Сообщение отправлено"}
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
        # Получаем сообщения между пользователями
        messages = get_messages_between_users(user["email"], other_user_email, job_id)
        messages = [dict(msg) if isinstance(msg, sqlite3.Row) else msg for msg in messages]
        
        # Фильтруем только новые сообщения (с ID больше last_message_id)
        new_messages = [msg for msg in messages if msg["id"] > last_message_id]
        
        # Отмечаем сообщения как прочитанные
        if new_messages:
            mark_messages_as_read(other_user_email, user["email"], job_id)
        
        return {
            "status": "success",
            "messages": new_messages,
            "last_message_id": max([msg["id"] for msg in messages]) if messages else 0
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- Страница сообщений ---
@app.get("/messages")
async def messages_get(request: Request, user: dict = Depends(require_login)):
    conversations = get_user_conversations(user["email"])
    conversations = [dict(conv) if isinstance(conv, sqlite3.Row) else conv for conv in conversations]
    
    return templates.TemplateResponse("messages.html", {
        "request": request,
        "user": user,
        "conversations": conversations
    })


# --- Чат с конкретным пользователем ---
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
    mark_messages_as_read(other_user_email, user["email"], job_id)
    
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "user": user,
        "other_user": other_user,
        "messages": messages,
        "job_id": job_id
    })


# --- Проектный чат ---
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
            if app["status"] == "accepted":
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
    mark_messages_as_read(other_user_email, user["email"], job_id)
    
    return templates.TemplateResponse("project_chat.html", {
        "request": request,
        "user": user,
        "other_user": other_user,
        "job": job,
        "messages": messages
    })


# --- Страницы профилей пользователей ---
@app.get("/profiles/freelancers")
async def freelancers_profiles_get(request: Request, user: dict = Depends(require_login)):
    freelancers = get_users_by_role("freelancer")
    freelancers = [dict(f) if isinstance(f, sqlite3.Row) else f for f in freelancers]
    
    return templates.TemplateResponse("profiles_freelancers.html", {
        "request": request,
        "user": user,
        "freelancers": freelancers
    })


@app.get("/profiles/clients")
async def clients_profiles_get(request: Request, user: dict = Depends(require_login)):
    clients = get_users_by_role("client")
    clients = [dict(c) if isinstance(c, sqlite3.Row) else c for c in clients]
    
    return templates.TemplateResponse("profiles_clients.html", {
        "request": request,
        "user": user,
        "clients": clients
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


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
