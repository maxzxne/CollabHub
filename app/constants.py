# Константы для приложения CollabHub

# Статусы проектов
JOB_STATUS_OPEN = "open"
JOB_STATUS_IN_PROGRESS = "in_progress"
JOB_STATUS_DONE = "done"
JOB_STATUS_COMPLETED = "completed"

# Понятные названия статусов для UI
JOB_STATUS_LABELS = {
    'open': 'В поисках исполнителя',
    'in_progress': 'В работе',
    'done': 'Завершен',
    'completed': 'Завершен'
}

# Приоритеты проектов
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"

# Роли пользователей
ROLE_CLIENT = "client"
ROLE_FREELANCER = "freelancer"

# Статусы откликов
APPLICATION_STATUS_PENDING = "pending"
APPLICATION_STATUS_ACCEPTED = "accepted"
APPLICATION_STATUS_REJECTED = "rejected"
APPLICATION_STATUS_COMPLETED = "completed"

# Пути к файлам
DEFAULT_AVATAR_PATH = "/static/defaultAvatar.jpg"
UPLOAD_DIR = "uploads"
AVATARS_DIR = "uploads/avatars"
PROJECTS_DIR = "uploads/projects"
PORTFOLIO_DIR = "uploads/portfolio"

# Разрешенные расширения файлов
ALLOWED_FILE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt'}

# Максимальный размер файла (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# JWT настройки
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 30

# Сообщения об ошибках
ERROR_MESSAGES = {
    'user_not_found': 'Пользователь не найден',
    'invalid_password': 'Неверный пароль',
    'email_exists': 'Email уже зарегистрирован',
    'invalid_file_type': 'Неподдерживаемый тип файла',
    'file_too_large': 'Файл слишком большой',
    'invalid_date': 'Некорректная дата',
    'access_denied': 'Нет доступа',
    'job_not_found': 'Проект не найден',
    'application_not_found': 'Заявка не найдена',
    'invalid_rating': 'Рейтинг должен быть от 1 до 5',
    'no_accepted_freelancer': 'Нет принятого фрилансера',
    'already_reviewed': 'Отзыв уже оставлен',
    'empty_comment': 'Комментарий не может быть пустым',
    'cannot_comment': 'Нет доступа к комментированию'
}

# Сообщения об успехе
SUCCESS_MESSAGES = {
    'profile_updated': 'Профиль успешно обновлен!',
    'message_sent': 'Сообщение отправлено',
    'review_created': 'Отзыв создан',
    'application_submitted': 'Отклик отправлен',
    'job_created': 'Проект создан',
    'job_updated': 'Проект обновлен',
    'job_deleted': 'Проект удален'
}

# Настройки пагинации
ITEMS_PER_PAGE = 12
MAX_PAGES_DISPLAY = 5

# Настройки чата
MESSAGES_PER_PAGE = 50
MESSAGE_MAX_LENGTH = 1000

# Настройки отзывов
MIN_RATING = 1
MAX_RATING = 5
REVIEW_COMMENT_MAX_LENGTH = 500
