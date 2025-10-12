"""
Конфигурация тестов для CollabHub
"""
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path

# Добавляем путь к приложению
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))

from database import init_db, get_connection
from models import create_user, get_user_by_email


@pytest.fixture
def test_db():
    """Создает временную базу данных для тестов"""
    # Создаем временный файл БД
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Инициализируем БД
    os.environ['DATABASE_URL'] = db_path
    init_db()
    
    yield db_path
    
    # Очищаем после тестов
    os.unlink(db_path)


@pytest.fixture
def test_user(test_db):
    """Создает тестового пользователя"""
    user_data = {
        'email': 'test@example.com',
        'password': 'test123',
        'name': 'Test User',
        'role': 'client'
    }
    
    create_user(**user_data)
    return user_data


@pytest.fixture
def test_freelancer(test_db):
    """Создает тестового фрилансера"""
    user_data = {
        'email': 'freelancer@example.com',
        'password': 'test123',
        'name': 'Test Freelancer',
        'role': 'freelancer'
    }
    
    create_user(**user_data)
    return user_data
