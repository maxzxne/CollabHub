"""
Тесты для API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Добавляем путь к приложению
sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))

from main import app


class TestAPI:
    """Тесты API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Создает тестовый клиент"""
        return TestClient(app)
    
    def test_home_page(self, client):
        """Тест главной страницы"""
        response = client.get("/")
        assert response.status_code == 200
        assert "CollabHub" in response.text
    
    def test_login_page(self, client):
        """Тест страницы входа"""
        response = client.get("/login")
        assert response.status_code == 302  # Redirect to home
    
    def test_register_page(self, client):
        """Тест страницы регистрации"""
        response = client.get("/register")
        assert response.status_code == 302  # Redirect to home
    
    def test_create_job_page_unauthorized(self, client):
        """Тест страницы создания проекта без авторизации"""
        response = client.get("/jobs/create")
        assert response.status_code == 302  # Redirect to login
    
    def test_profile_page_unauthorized(self, client):
        """Тест страницы профиля без авторизации"""
        response = client.get("/profile")
        assert response.status_code == 302  # Redirect to login
