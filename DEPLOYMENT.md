# 🚀 Инструкция по развертыванию

## Локальная разработка

### 1. Подготовка окружения
```bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/diplom_birja.git
cd diplom_birja

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Перейдите в папку backend
cd backend

# Установите зависимости
pip install -r requirements.txt
```

### 2. Запуск приложения
```bash
python main.py
```

Приложение будет доступно по адресу: `http://localhost:8000`

## Развертывание на сервере

### 1. Подготовка сервера
```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Python и pip
sudo apt install python3 python3-pip python3-venv -y

# Установите nginx (опционально)
sudo apt install nginx -y
```

### 2. Клонирование и настройка
```bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/diplom_birja.git
cd diplom_birja

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
cd backend
pip install -r requirements.txt
```

### 3. Настройка systemd сервиса
Создайте файл `/etc/systemd/system/collabhub.service`:

```ini
[Unit]
Description=CollabHub FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/diplom_birja/backend
Environment="PATH=/path/to/your/diplom_birja/venv/bin"
ExecStart=/path/to/your/diplom_birja/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Запуск сервиса
```bash
# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите сервис
sudo systemctl enable collabhub

# Запустите сервис
sudo systemctl start collabhub

# Проверьте статус
sudo systemctl status collabhub
```

### 5. Настройка Nginx (опционально)
Создайте файл `/etc/nginx/sites-available/collabhub`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/diplom_birja/backend/static;
    }

    location /uploads {
        alias /path/to/your/diplom_birja/backend/uploads;
    }
}
```

Активируйте конфигурацию:
```bash
sudo ln -s /etc/nginx/sites-available/collabhub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Развертывание на Heroku

### 1. Подготовка файлов
Создайте файл `Procfile` в корне проекта:
```
web: cd backend && python main.py
```

Создайте файл `runtime.txt`:
```
python-3.11.0
```

### 2. Развертывание
```bash
# Установите Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Войдите в Heroku
heroku login

# Создайте приложение
heroku create your-app-name

# Добавьте переменные окружения
heroku config:set SECRET_KEY=your-secret-key

# Разверните приложение
git push heroku main
```

## Развертывание на Docker

### 1. Создайте Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["python", "main.py"]
```

### 2. Создайте docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./backend/uploads:/app/uploads
    environment:
      - SECRET_KEY=your-secret-key
```

### 3. Запуск
```bash
docker-compose up -d
```

## 🔧 Настройка после развертывания

### 1. Создание администратора
После первого запуска создайте администратора через базу данных или добавьте соответствующий код.

### 2. Настройка файлов
Убедитесь, что папка `uploads` имеет правильные права доступа:
```bash
chmod 755 backend/uploads
chown www-data:www-data backend/uploads
```

### 3. Резервное копирование
Настройте регулярное резервное копирование базы данных:
```bash
# Создайте скрипт backup.sh
#!/bin/bash
cp backend/freelance.db backup/freelance_$(date +%Y%m%d_%H%M%S).db
```

## 📊 Мониторинг

### Логи приложения
```bash
# Просмотр логов systemd
sudo journalctl -u collabhub -f

# Просмотр логов nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Мониторинг ресурсов
```bash
# Использование памяти и CPU
htop

# Использование диска
df -h

# Статус сервисов
sudo systemctl status collabhub nginx
```

## 🔒 Безопасность

### 1. Настройка файрвола
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. SSL сертификат (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Регулярные обновления
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление зависимостей Python
pip install --upgrade -r requirements.txt
```
