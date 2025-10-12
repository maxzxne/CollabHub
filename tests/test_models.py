"""
Тесты для моделей данных
"""
import pytest
from models import create_job, get_job_by_id, apply_to_job, get_applications


class TestModels:
    """Тесты моделей данных"""
    
    def test_create_job(self, test_user):
        """Тест создания проекта"""
        job_data = {
            'title': 'Test Project',
            'description': 'Test description',
            'budget': 1000,
            'deadline': '2025-12-31',
            'creator_email': test_user['email']
        }
        
        job_id = create_job(**job_data)
        assert job_id is not None
        
        # Проверяем, что проект создан
        job = get_job_by_id(job_id)
        assert job is not None
        assert job['title'] == job_data['title']
        assert job['description'] == job_data['description']
        assert job['budget'] == job_data['budget']
        assert job['creator_email'] == job_data['creator_email']
    
    def test_apply_to_job(self, test_user, test_freelancer):
        """Тест отклика на проект"""
        # Создаем проект
        job_id = create_job(
            title='Test Project',
            description='Test description',
            budget=1000,
            deadline='2025-12-31',
            creator_email=test_user['email']
        )
        
        # Откликаемся на проект
        application_id = apply_to_job(job_id, test_freelancer['email'])
        assert application_id is not None
        
        # Проверяем отклик
        applications = get_applications(job_id)
        assert len(applications) == 1
        assert applications[0]['freelancer_email'] == test_freelancer['email']
        assert applications[0]['job_id'] == job_id
    
    def test_get_job_by_id(self, test_user):
        """Тест получения проекта по ID"""
        # Создаем проект
        job_id = create_job(
            title='Test Project',
            description='Test description',
            budget=1000,
            deadline='2025-12-31',
            creator_email=test_user['email']
        )
        
        # Получаем проект
        job = get_job_by_id(job_id)
        assert job is not None
        assert job['id'] == job_id
        
        # Несуществующий проект
        job = get_job_by_id(99999)
        assert job is None
