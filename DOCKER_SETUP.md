# Локальный запуск через Docker

## Быстрый старт

1. **Соберите и запустите контейнер:**
   ```bash
   docker-compose up --build
   ```

2. **Откройте приложение в браузере:**
   ```
   http://localhost:10000
   ```

## Команды для управления

### Запуск
```bash
# Сборка и запуск
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d --build

# Только сборка без запуска
docker-compose build
```

### Остановка
```bash
# Остановка контейнеров
docker-compose down

# Остановка с удалением volumes
docker-compose down -v
```

### Просмотр логов
```bash
# Все логи
docker-compose logs

# Логи в реальном времени
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs freelance-app
```

### Перезапуск
```bash
# Перезапуск контейнера
docker-compose restart

# Перезапуск с пересборкой
docker-compose up --build
```

## Структура файлов

- `Dockerfile` - конфигурация Docker-образа
- `docker-compose.yml` - настройки для запуска
- `.dockerignore` - файлы, исключаемые из сборки

## Важные особенности

1. **База данных**: SQLite файл монтируется как volume, данные сохраняются между перезапусками
2. **Загруженные файлы**: Папка `uploads` монтируется как volume
3. **Порт**: Приложение доступно на порту 10000
4. **Автоперезапуск**: Контейнер автоматически перезапускается при сбоях

## Отладка

### Вход в контейнер
```bash
docker-compose exec freelance-app bash
```

### Проверка статуса
```bash
docker-compose ps
```

### Очистка
```bash
# Удаление всех контейнеров и образов
docker-compose down --rmi all

# Полная очистка Docker
docker system prune -a
```

## Безопасность

- Этот Docker-набор предназначен только для локальной разработки
- Не используйте эти настройки в продакшене
- Для продакшена используйте настройки из `RENDER_DEPLOY.md`
