from database import get_connection
from passlib.hash import bcrypt
import sqlite3
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os


def get_user(email, password):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Users WHERE email=? AND password=?", (email, password))
	user = cursor.fetchone()
	conn.close()
	return user

def get_jobs(status=None):
	conn = get_connection()
	cursor = conn.cursor()
	if status:
		cursor.execute("SELECT * FROM Jobs WHERE status = ?", (status,))
	else:
		cursor.execute("SELECT * FROM Jobs")
	jobs = cursor.fetchall()
	conn.close()
	return jobs




# JWT настройки
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Хэширование пароля
def hash_password(password: str) -> str:
	return bcrypt.hash(password)

# Проверка пароля
def verify_password(password: str, hashed: str) -> bool:
	return bcrypt.verify(password, hashed)

# JWT функции
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


def get_user_by_email(email):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Users WHERE email= ?", (email,))
	user = cursor.fetchone()
	conn.close()
	return user



def create_user(email: str, hashed_password: str, role: str, name: str | None = None, avatar: str | None = None):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute(
		"INSERT INTO Users (email, password, role, name, avatar) VALUES (?, ?, ?, ?, ?)",
		(email, hashed_password, role, name, avatar),
	)
	conn.commit()
	conn.close()


def update_user_profile(user_id: int, name: str = None, about_me: str = None, activity: str = None, 
                       skills: str = None, phone: str = None, telegram: str = None, avatar: str = None, 
                       email: str = None, portfolio_files: str = None, portfolio_links: str = None):
	conn = get_connection()
	cursor = conn.cursor()
	
	# Строим динамический запрос только для переданных полей
	updates = []
	params = []
	
	if name is not None:
		updates.append("name = ?")
		params.append(name)
	if about_me is not None:
		updates.append("about_me = ?")
		params.append(about_me)
	if activity is not None:
		updates.append("activity = ?")
		params.append(activity)
	if skills is not None:
		updates.append("skills = ?")
		params.append(skills)
	if phone is not None:
		updates.append("phone = ?")
		params.append(phone)
	if telegram is not None:
		updates.append("telegram = ?")
		params.append(telegram)
	if avatar is not None:
		updates.append("avatar = ?")
		params.append(avatar)
	if email is not None:
		updates.append("email = ?")
		params.append(email)
	if portfolio_files is not None:
		updates.append("portfolio_files = ?")
		params.append(portfolio_files)
	if portfolio_links is not None:
		updates.append("portfolio_links = ?")
		params.append(portfolio_links)
	
	if updates:
		params.append(user_id)
		query = f"UPDATE Users SET {', '.join(updates)} WHERE id = ?"
		cursor.execute(query, params)
		conn.commit()
	
	conn.close()


def get_user_by_id(user_id: int):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
	user = cursor.fetchone()
	conn.close()
	return user


def create_job(title, description, deadline, creator_email, status="open", priority: str = "medium", files: list = None):
	conn = get_connection()
	cursor = conn.cursor()
	
	# Конвертируем список файлов в JSON строку
	files_json = None
	if files:
		import json
		files_json = json.dumps(files)
	
	cursor.execute(
		"INSERT INTO Jobs (title, description, deadline, status, creator_email, priority, files) VALUES (?, ?, ?, ?, ?, ?, ?)",
		(title, description, deadline, status, creator_email, priority, files_json)
	)
	conn.commit()
	conn.close()


def update_job(job_id, title, description, deadline, status, priority: str = None):
	conn = get_connection()
	cursor = conn.cursor()
	if priority is None:
		cursor.execute(
			"UPDATE Jobs SET title=?, description=?, deadline=?, status=? WHERE id=?",
			(title, description, deadline, status, job_id)
		)
	else:
		cursor.execute(
			"UPDATE Jobs SET title=?, description=?, deadline=?, status=?, priority=? WHERE id=?",
			(title, description, deadline, status, priority, job_id)
		)
	conn.commit()
	conn.close()

def delete_job(job_id):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Jobs WHERE id=?", (job_id,))
	conn.commit()
	conn.close()
	return True

def get_job_by_id(job_id):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Jobs WHERE id=?", (job_id,))
	job = cursor.fetchone()
	conn.close()
	return job



def apply_to_job(job_id: int, freelancer_email: str):
	conn = get_connection()
	cursor = conn.cursor()
	try:
		cursor.execute(
			"INSERT INTO Applications (job_id, freelancer_email) VALUES (?, ?)",
			(job_id, freelancer_email)
		)
		conn.commit()
		return True
	except sqlite3.IntegrityError:
		return False
	finally:
		conn.close()

def get_applications(job_id: int):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("""
		SELECT a.*, u.name as freelancer_name
		FROM Applications a 
		LEFT JOIN Users u ON a.freelancer_email = u.email
		WHERE a.job_id = ?
		ORDER BY a.id DESC
	""", (job_id,))
	apps = cursor.fetchall()
	conn.close()
	return apps


def get_applications_by_freelancer(freelancer_email: str):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("""
		SELECT a.*, j.title, j.status as job_status, j.creator_email 
		FROM Applications a 
		JOIN Jobs j ON a.job_id = j.id 
		WHERE a.freelancer_email = ?
		ORDER BY a.id DESC
	""", (freelancer_email,))
	apps = cursor.fetchall()
	conn.close()
	return apps


def get_applications_for_client(creator_email: str):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("""
		SELECT a.*, j.title, j.status as job_status, u.name as freelancer_name, u.about_me, u.skills
		FROM Applications a 
		JOIN Jobs j ON a.job_id = j.id 
		JOIN Users u ON a.freelancer_email = u.email
		WHERE j.creator_email = ?
		ORDER BY a.id DESC
	""", (creator_email,))
	apps = cursor.fetchall()
	conn.close()
	return apps


def update_application_status(application_id: int, status: str):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("UPDATE Applications SET status = ? WHERE id = ?", (status, application_id))
	
	# Если заявка принята, обновляем статус проекта на "in_progress"
	if status == "accepted":
		cursor.execute("SELECT job_id FROM Applications WHERE id = ?", (application_id,))
		job_id = cursor.fetchone()['job_id']
		cursor.execute("UPDATE Jobs SET status = 'in_progress' WHERE id = ?", (job_id,))
	
	conn.commit()
	conn.close()


def get_application_by_id(application_id: int):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Applications WHERE id = ?", (application_id,))
	app = cursor.fetchone()
	conn.close()
	return app


def has_user_applied_to_job(job_id: int, freelancer_email: str):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("SELECT id FROM Applications WHERE job_id = ? AND freelancer_email = ?", (job_id, freelancer_email))
	result = cursor.fetchone()
	conn.close()
	return result is not None


def get_user_application_status(job_id: int, freelancer_email: str):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("SELECT status FROM Applications WHERE job_id = ? AND freelancer_email = ?", (job_id, freelancer_email))
	result = cursor.fetchone()
	conn.close()
	return result['status'] if result else None


def complete_job(job_id: int, freelancer_email: str):
	conn = get_connection()
	cursor = conn.cursor()
	# Обновляем статус проекта на "done"
	cursor.execute("UPDATE Jobs SET status = 'done' WHERE id = ?", (job_id,))
	# Обновляем статус отклика на "completed"
	cursor.execute("UPDATE Applications SET status = 'completed' WHERE job_id = ? AND freelancer_email = ?", (job_id, freelancer_email))
	
	# Обновляем статистику фрилансера после завершения проекта
	update_freelancer_stats(freelancer_email, cursor)
	
	conn.commit()
	conn.close()


def update_freelancer_stats(freelancer_email: str, cursor=None):
	"""Обновляет рейтинг и количество завершенных проектов для фрилансера"""
	if cursor is None:
		conn = get_connection()
		cursor = conn.cursor()
		should_close = True
	else:
		should_close = False
	
	# Получаем средний рейтинг
	cursor.execute("""
		SELECT AVG(rating) as avg_rating
		FROM Reviews 
		WHERE freelancer_email = ?
	""", (freelancer_email,))
	result = cursor.fetchone()
	
	# Считаем количество завершенных проектов
	cursor.execute("""
		SELECT COUNT(DISTINCT j.id) as completed_count
		FROM Jobs j
		INNER JOIN Applications a ON j.id = a.job_id
		WHERE a.freelancer_email = ? AND a.status = 'completed' AND j.status = 'done'
	""", (freelancer_email,))
	completed_result = cursor.fetchone()
	
	# Обновляем данные пользователя
	avg_rating = round(result['avg_rating'], 1) if result and result['avg_rating'] is not None else 0.0
	completed_projects = completed_result['completed_count'] if completed_result else 0
	
	cursor.execute("""
		UPDATE Users 
		SET rating = ?, completed_projects = ?
		WHERE email = ?
	""", (avg_rating, completed_projects, freelancer_email))
	
	print(f"Updated stats for {freelancer_email}: rating={avg_rating}, projects={completed_projects}")
	
	if should_close:
		conn.commit()
		conn.close()


def update_all_freelancer_stats():
	"""Обновляет статистику всех фрилансеров (для исправления существующих данных)"""
	conn = get_connection()
	cursor = conn.cursor()
	
	# Получаем всех фрилансеров
	cursor.execute("SELECT email FROM Users WHERE role = 'freelancer'")
	freelancers = cursor.fetchall()
	
	for freelancer in freelancers:
		update_freelancer_stats(freelancer['email'], cursor)
	
	conn.commit()
	conn.close()
	print(f"Updated stats for {len(freelancers)} freelancers")


def create_review(job_id: int, freelancer_email: str, client_email: str, rating: int, comment: str = None):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute(
		"INSERT INTO Reviews (job_id, freelancer_email, client_email, rating, comment) VALUES (?, ?, ?, ?, ?)",
		(job_id, freelancer_email, client_email, rating, comment)
	)
	
	# Обновляем статистику фрилансера после добавления отзыва
	update_freelancer_stats(freelancer_email, cursor)
	
	conn.commit()
	conn.close()


def get_reviews_for_freelancer(freelancer_email: str):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("""
		SELECT r.*, j.title, u.name as client_name
		FROM Reviews r
		JOIN Jobs j ON r.job_id = j.id
		JOIN Users u ON r.client_email = u.email
		WHERE r.freelancer_email = ?
		ORDER BY r.created_at DESC
	""", (freelancer_email,))
	reviews = cursor.fetchall()
	conn.close()
	return reviews


def get_job_reviews(job_id: int):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Reviews WHERE job_id = ?", (job_id,))
	reviews = cursor.fetchall()
	conn.close()
	return reviews


def has_reviewed_job(job_id: int, client_email: str, freelancer_email: str):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("SELECT id FROM Reviews WHERE job_id = ? AND client_email = ? AND freelancer_email = ?", 
	               (job_id, client_email, freelancer_email))
	result = cursor.fetchone()
	conn.close()
	return result is not None


# Функции для работы с сообщениями
def create_message(sender_email: str, receiver_email: str, message: str, job_id: int = None):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute(
		"INSERT INTO Messages (sender_email, receiver_email, job_id, message) VALUES (?, ?, ?, ?)",
		(sender_email, receiver_email, job_id, message)
	)
	conn.commit()
	conn.close()


def get_messages_between_users(user1_email: str, user2_email: str, job_id: int = None):
	conn = get_connection()
	cursor = conn.cursor()
	if job_id:
		cursor.execute("""
			SELECT m.*, u.name as sender_name, u.avatar as sender_avatar
			FROM Messages m
			JOIN Users u ON m.sender_email = u.email
			WHERE ((m.sender_email = ? AND m.receiver_email = ?) OR 
			       (m.sender_email = ? AND m.receiver_email = ?)) 
			AND m.job_id = ?
			ORDER BY m.created_at ASC
		""", (user1_email, user2_email, user2_email, user1_email, job_id))
	else:
		cursor.execute("""
			SELECT m.*, u.name as sender_name, u.avatar as sender_avatar
			FROM Messages m
			JOIN Users u ON m.sender_email = u.email
			WHERE ((m.sender_email = ? AND m.receiver_email = ?) OR 
			       (m.sender_email = ? AND m.receiver_email = ?)) 
			AND m.job_id IS NULL
			ORDER BY m.created_at ASC
		""", (user1_email, user2_email, user2_email, user1_email))
	messages = cursor.fetchall()
	conn.close()
	return messages


def get_user_conversations(user_email: str):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("""
		SELECT DISTINCT 
			CASE 
				WHEN sender_email = ? THEN receiver_email 
				ELSE sender_email 
			END as other_user_email,
			u.name as other_user_name,
			u.avatar as other_user_avatar,
			MAX(m.created_at) as last_message_time,
			COUNT(CASE WHEN m.receiver_email = ? AND m.is_read = FALSE THEN 1 END) as unread_count
		FROM Messages m
		JOIN Users u ON (CASE WHEN m.sender_email = ? THEN m.receiver_email ELSE m.sender_email END) = u.email
		WHERE m.sender_email = ? OR m.receiver_email = ?
		GROUP BY other_user_email, other_user_name, other_user_avatar
		ORDER BY last_message_time DESC
	""", (user_email, user_email, user_email, user_email, user_email))
	conversations = cursor.fetchall()
	conn.close()
	return conversations


def mark_messages_as_read(current_user_email: str, other_user_email: str, job_id: int = None):
	"""Отмечает как прочитанные сообщения, где current_user_email является получателем"""
	conn = get_connection()
	cursor = conn.cursor()
	if job_id:
		cursor.execute("""
			UPDATE Messages 
			SET is_read = TRUE 
			WHERE sender_email = ? AND receiver_email = ? AND job_id = ?
		""", (other_user_email, current_user_email, job_id))
	else:
		cursor.execute("""
			UPDATE Messages 
			SET is_read = TRUE 
			WHERE sender_email = ? AND receiver_email = ? AND job_id IS NULL
		""", (other_user_email, current_user_email))
	
	conn.commit()
	conn.close()


def get_unread_messages_count(user_email: str):
	"""Получает общее количество непрочитанных сообщений для пользователя"""
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("""
		SELECT COUNT(*) as unread_count
		FROM Messages 
		WHERE receiver_email = ? AND is_read = FALSE
	""", (user_email,))
	result = cursor.fetchone()
	conn.close()
	return result['unread_count'] if result else 0


# Функции для работы с профилями пользователей
def get_users_by_role(role: str):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Users WHERE role = ? ORDER BY rating DESC, completed_projects DESC", (role,))
	users = cursor.fetchall()
	conn.close()
	return users


def get_all_users_with_filters(role_filter: str = None, min_rating: str = None):
	"""Получает всех пользователей с возможностью фильтрации"""
	conn = get_connection()
	cursor = conn.cursor()
	
	query = "SELECT * FROM Users WHERE 1=1"
	params = []
	
	if role_filter and role_filter != "all":
		query += " AND role = ?"
		params.append(role_filter)
	
	if min_rating and min_rating.strip():
		try:
			rating_value = float(min_rating)
			query += " AND rating >= ?"
			params.append(rating_value)
		except ValueError:
			pass
	
	query += " ORDER BY rating DESC, completed_projects DESC"
	
	cursor.execute(query, params)
	users = cursor.fetchall()
	conn.close()
	return users


def get_user_profile_by_email(email: str):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
	user = cursor.fetchone()
	conn.close()
	return user


# Функции для работы с комментариями к проектам
def create_project_comment(job_id: int, user_email: str, comment: str):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute(
		"INSERT INTO ProjectComments (job_id, user_email, comment) VALUES (?, ?, ?)",
		(job_id, user_email, comment)
	)
	conn.commit()
	conn.close()


def get_project_comments(job_id: int):
	conn = get_connection()
	cursor = conn.cursor()
	cursor.execute("""
		SELECT c.*, u.name as user_name, u.avatar as user_avatar
		FROM ProjectComments c
		JOIN Users u ON c.user_email = u.email
		WHERE c.job_id = ?
		ORDER BY c.created_at ASC
	""", (job_id,))
	comments = cursor.fetchall()
	conn.close()
	return comments


def can_user_comment_on_project(job_id: int, user_email: str):
	"""Проверяет, может ли пользователь комментировать проект (только участники)"""
	conn = get_connection()
	cursor = conn.cursor()
	
	# Получаем проект
	cursor.execute("SELECT creator_email FROM Jobs WHERE id = ?", (job_id,))
	job = cursor.fetchone()
	if not job:
		conn.close()
		return False
	
	# Проверяем, является ли пользователь создателем проекта
	if job['creator_email'] == user_email:
		conn.close()
		return True
	
	# Проверяем, является ли пользователь принятым фрилансером
	cursor.execute("""
		SELECT id FROM Applications 
		WHERE job_id = ? AND freelancer_email = ? AND status IN ('accepted', 'completed')
	""", (job_id, user_email))
	application = cursor.fetchone()
	
	conn.close()
	return application is not None


def get_project_participants(job_id: int):
	"""Получает всех участников проекта (создатель + принятые фрилансеры)"""
	conn = get_connection()
	cursor = conn.cursor()
	
	# Получаем создателя проекта
	cursor.execute("""
		SELECT j.creator_email, u.name, u.avatar, u.role
		FROM Jobs j
		JOIN Users u ON j.creator_email = u.email
		WHERE j.id = ?
	""", (job_id,))
	creator = cursor.fetchone()
	
	# Получаем принятых фрилансеров
	cursor.execute("""
		SELECT a.freelancer_email, u.name, u.avatar, u.role, a.status
		FROM Applications a
		JOIN Users u ON a.freelancer_email = u.email
		WHERE a.job_id = ? AND a.status IN ('accepted', 'completed')
	""", (job_id,))
	freelancers = cursor.fetchall()
	
	conn.close()
	
	participants = []
	if creator:
		participants.append(dict(creator))
	
	for freelancer in freelancers:
		participants.append(dict(freelancer))
	
	return participants






