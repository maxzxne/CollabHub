# Утилиты для работы с данными и форматированием
import sqlite3
import json
from typing import Dict, List, Any, Optional


def convert_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Конвертирует sqlite3.Row в обычный словарь"""
    if isinstance(row, sqlite3.Row):
        return dict(row)
    return row


def convert_rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    """Конвертирует список sqlite3.Row в список словарей"""
    return [convert_row_to_dict(row) for row in rows]


def parse_json_field(field_value: Optional[str]) -> List[str]:
    """Парсит JSON поле в список строк"""
    if not field_value:
        return []
    try:
        return json.loads(field_value)
    except (json.JSONDecodeError, TypeError):
        return []


def format_user_data(user: sqlite3.Row) -> Dict[str, Any]:
    """Форматирует данные пользователя для использования в шаблонах"""
    user_dict = convert_row_to_dict(user)
    
    # Устанавливаем аватар по умолчанию
    if not user_dict.get("avatar"):
        user_dict["avatar"] = "/static/defaultAvatar.jpg"
    
    # Парсим JSON поля
    user_dict["portfolio_files"] = parse_json_field(user_dict.get("portfolio_files"))
    
    return user_dict


def format_job_data(job: sqlite3.Row) -> Dict[str, Any]:
    """Форматирует данные проекта для использования в шаблонах"""
    job_dict = convert_row_to_dict(job)
    
    # Парсим файлы проекта
    if job_dict.get("files"):
        job_dict["files"] = parse_json_field(job_dict["files"])
    else:
        job_dict["files"] = []
    
    return job_dict


def get_status_badge_class(status: str) -> str:
    """Возвращает CSS классы для бейджа статуса"""
    status_classes = {
        'open': 'bg-green-50 text-green-700 border border-green-200',
        'in_progress': 'bg-yellow-50 text-yellow-700 border border-yellow-200',
        'done': 'bg-gray-100 text-gray-600 border border-gray-300',
        'completed': 'bg-gray-100 text-gray-600 border border-gray-300'
    }
    return status_classes.get(status, 'bg-gray-50 text-gray-600 border border-gray-200')


def get_priority_badge_class(priority: str) -> str:
    """Возвращает CSS классы для бейджа приоритета"""
    priority_classes = {
        'high': 'bg-red-50 text-red-700 border border-red-200',
        'low': 'bg-gray-50 text-gray-600 border border-gray-200',
        'medium': 'bg-blue-50 text-blue-700 border border-blue-200'
    }
    return priority_classes.get(priority, 'bg-blue-50 text-blue-700 border border-blue-200')


def get_status_text(status: str) -> str:
    """Возвращает читаемый текст статуса"""
    status_texts = {
        'open': 'Открыт',
        'in_progress': 'В работе',
        'done': 'Завершен',
        'completed': 'Завершен'
    }
    return status_texts.get(status, status)


def get_priority_text(priority: str) -> str:
    """Возвращает читаемый текст приоритета"""
    priority_texts = {
        'high': 'Высокий',
        'low': 'Низкий',
        'medium': 'Средний'
    }
    return priority_texts.get(priority, 'Средний')


def validate_email(email: str) -> bool:
    """Простая валидация email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """Валидация пароля"""
    if len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов"
    if len(password) > 100:
        return False, "Пароль слишком длинный"
    return True, ""


def sanitize_input(text: str) -> str:
    """Очищает пользовательский ввод от потенциально опасных символов"""
    if not text:
        return ""
    # Убираем HTML теги и экранируем специальные символы
    import html
    return html.escape(text.strip())
