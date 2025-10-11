#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных в CollabHub
Создает пользователей, проекты, отклики, отзывы, сообщения и комментарии
"""

import sqlite3
import random
from datetime import datetime, timedelta
from passlib.hash import bcrypt
import os
import sys

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection
from models import hash_password

def clear_database():
    """Очищает базу данных от существующих данных"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Удаляем данные в правильном порядке (с учетом внешних ключей)
    tables = ['Messages', 'Reviews', 'Applications', 'ProjectComments', 'Jobs', 'Users']
    
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        print(f"Очищена таблица {table}")
    
    conn.commit()
    conn.close()
    print("База данных очищена!")

def create_test_users():
    """Создает тестовых пользователей"""
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
    
    for user in users:
        hashed_password = hash_password("test123")  # Общий пароль для всех тестовых пользователей
        
        cursor.execute("""
            INSERT INTO Users (email, password, role, name, about_me, activity, skills, phone, telegram, rating, completed_projects)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user['email'],
            hashed_password,
            user['role'],
            user['name'],
            user['about_me'],
            user['activity'],
            user['skills'],
            user['phone'],
            user['telegram'],
            user.get('rating'),
            user.get('completed_projects')
        ))
    
    conn.commit()
    conn.close()
    print(f"Создано {len(users)} тестовых пользователей")

def create_test_jobs():
    """Создает тестовые проекты"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Получаем клиентов
    cursor.execute("SELECT email FROM Users WHERE role = 'client'")
    clients = [row[0] for row in cursor.fetchall()]
    
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
    
    for job in jobs:
        cursor.execute("""
            INSERT INTO Jobs (title, description, deadline, priority, status, creator_email, files)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            job['title'],
            job['description'],
            job['deadline'],
            job['priority'],
            job['status'],
            job['creator_email'],
            job['files']
        ))
    
    conn.commit()
    conn.close()
    print(f"Создано {len(jobs)} тестовых проектов")

def create_test_applications():
    """Создает тестовые отклики на проекты"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Получаем фрилансеров и проекты
    cursor.execute("SELECT email FROM Users WHERE role = 'freelancer'")
    freelancers = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM Jobs")
    jobs = [row[0] for row in cursor.fetchall()]
    
    # Создаем отклики
    applications = [
        # Открытые проекты
        {'job_id': 1, 'freelancer_email': freelancers[0], 'status': 'pending'},
        {'job_id': 1, 'freelancer_email': freelancers[3], 'status': 'pending'},
        {'job_id': 3, 'freelancer_email': freelancers[2], 'status': 'pending'},
        {'job_id': 3, 'freelancer_email': freelancers[0], 'status': 'pending'},
        {'job_id': 5, 'freelancer_email': freelancers[1], 'status': 'pending'},
        {'job_id': 5, 'freelancer_email': freelancers[3], 'status': 'pending'},
        {'job_id': 8, 'freelancer_email': freelancers[1], 'status': 'pending'},
        {'job_id': 8, 'freelancer_email': freelancers[3], 'status': 'pending'},
        
        # Проекты в работе
        {'job_id': 2, 'freelancer_email': freelancers[0], 'status': 'accepted'},
        {'job_id': 6, 'freelancer_email': freelancers[3], 'status': 'accepted'},
        
        # Завершенные проекты
        {'job_id': 4, 'freelancer_email': freelancers[4], 'status': 'completed'},
        {'job_id': 7, 'freelancer_email': freelancers[2], 'status': 'completed'},
    ]
    
    for app in applications:
        cursor.execute("""
            INSERT INTO Applications (job_id, freelancer_email, status)
            VALUES (?, ?, ?)
        """, (app['job_id'], app['freelancer_email'], app['status']))
    
    conn.commit()
    conn.close()
    print(f"Создано {len(applications)} тестовых откликов")

def create_test_reviews():
    """Создает тестовые отзывы"""
    conn = get_connection()
    cursor = conn.cursor()
    
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
            review['job_id'],
            review['freelancer_email'],
            review['client_email'],
            review['rating'],
            review['comment']
        ))
    
    conn.commit()
    conn.close()
    print(f"Создано {len(reviews)} тестовых отзывов")

def create_test_messages():
    """Создает тестовые сообщения"""
    conn = get_connection()
    cursor = conn.cursor()
    
    messages = [
        # Сообщения по проекту в работе
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
        
        # Сообщения по завершенному проекту
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
        
        # Обычные сообщения (не по проекту)
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
            msg['sender_email'],
            msg['receiver_email'],
            msg['job_id'],
            msg['message'],
            msg['created_at']
        ))
    
    conn.commit()
    conn.close()
    print(f"Создано {len(messages)} тестовых сообщений")

def create_test_comments():
    """Создает тестовые комментарии к проектам"""
    conn = get_connection()
    cursor = conn.cursor()
    
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
            comment['job_id'],
            comment['user_email'],
            comment['comment'],
            comment['created_at']
        ))
    
    conn.commit()
    conn.close()
    print(f"Создано {len(comments)} тестовых комментариев")

def main():
    """Основная функция для создания всех тестовых данных"""
    print("Создание тестовых данных для CollabHub...")
    print("=" * 50)
    
    # Очищаем базу данных
    clear_database()
    
    # Создаем тестовые данные
    create_test_users()
    create_test_jobs()
    create_test_applications()
    create_test_reviews()
    create_test_messages()
    create_test_comments()
    
    print("=" * 50)
    print("Все тестовые данные созданы успешно!")
    print("\nИнформация для входа:")
    print("Клиенты:")
    print("  - client1@test.com / test123")
    print("  - client2@test.com / test123")
    print("  - client3@test.com / test123")
    print("\nФрилансеры:")
    print("  - freelancer1@test.com / test123")
    print("  - freelancer2@test.com / test123")
    print("  - freelancer3@test.com / test123")
    print("  - freelancer4@test.com / test123")
    print("  - freelancer5@test.com / test123")
    print("\nСистема сообщений использует polling каждые 3 секунды")
    print("Есть проекты в разных статусах, отклики, отзывы и комментарии")

if __name__ == "__main__":
    main()
