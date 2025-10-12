"""
Тесты для функций авторизации
"""
import pytest
from models import create_user, get_user_by_email, verify_password


class TestAuth:
    """Тесты авторизации"""
    
    def test_create_user(self, test_db):
        """Тест создания пользователя"""
        user_data = {
            'email': 'test@example.com',
            'password': 'test123',
            'name': 'Test User',
            'role': 'client'
        }
        
        # Создаем пользователя
        user_id = create_user(**user_data)
        assert user_id is not None
        
        # Проверяем, что пользователь создан
        user = get_user_by_email(user_data['email'])
        assert user is not None
        assert user['email'] == user_data['email']
        assert user['name'] == user_data['name']
        assert user['role'] == user_data['role']
    
    def test_verify_password(self, test_user):
        """Тест проверки пароля"""
        # Правильный пароль
        assert verify_password('test123', test_user['email']) is True
        
        # Неправильный пароль
        assert verify_password('wrong_password', test_user['email']) is False
    
    def test_get_user_by_email(self, test_user):
        """Тест получения пользователя по email"""
        # Существующий пользователь
        user = get_user_by_email(test_user['email'])
        assert user is not None
        assert user['email'] == test_user['email']
        
        # Несуществующий пользователь
        user = get_user_by_email('nonexistent@example.com')
        assert user is None
    
    def test_create_duplicate_user(self, test_user):
        """Тест создания дублирующегося пользователя"""
        with pytest.raises(Exception):
            create_user(
                email=test_user['email'],
                password='test123',
                name='Another User',
                role='client'
            )
