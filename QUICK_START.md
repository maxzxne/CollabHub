# ⚡ Быстрый старт - Загрузка на GitHub

## 🎯 Что нужно сделать

### 1. Создать репозиторий на GitHub
1. Зайдите на [github.com](https://github.com)
2. Нажмите "New repository"
3. Название: `diplom_birja` (или любое другое)
4. Описание: "CollabHub - Биржа фриланса"
5. Выберите "Public" или "Private"
6. **НЕ** ставьте галочки на "Add a README file", "Add .gitignore", "Choose a license"
7. Нажмите "Create repository"

### 2. Инициализация Git в проекте
```bash
# В корневой папке проекта (C:\Projects\diplom_birja)
git init
git add .
git commit -m "Initial commit: CollabHub freelance platform"
```

### 3. Подключение к GitHub
```bash
# Замените yourusername на ваш GitHub username
git remote add origin https://github.com/yourusername/diplom_birja.git
git branch -M main
git push -u origin main
```

## ✅ Готово!

Теперь ваш проект на GitHub. Дальше работайте как обычно:

```bash
# Добавить изменения
git add .
git commit -m "Описание изменений"
git push
```

## 🔧 Что с виртуальным окружением?

**НЕ загружайте папку `venv/` в Git!** 

В файле `.gitignore` уже настроено игнорирование:
- `venv/`
- `.venv/`
- `__pycache__/`
- `*.db`
- `uploads/` (содержимое)

## 📁 Что загружается в Git:

✅ **Загружается:**
- Весь код Python (`backend/`)
- HTML шаблоны (`templates/`)
- CSS и JS (`static/`)
- Конфигурационные файлы
- README.md и документация

❌ **НЕ загружается:**
- Виртуальное окружение (`venv/`)
- База данных (`*.db`)
- Загруженные файлы (`uploads/`)
- Кэш Python (`__pycache__/`)

## 🚀 Как другие будут запускать проект:

1. Клонируют репозиторий
2. Создают свое виртуальное окружение
3. Устанавливают зависимости из `requirements.txt`
4. Запускают приложение

```bash
git clone https://github.com/yourusername/diplom_birja.git
cd diplom_birja
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r backend/requirements.txt
cd backend
python main.py
```

## 📋 Файлы для GitHub:

- ✅ `.gitignore` - что игнорировать
- ✅ `README.md` - описание проекта
- ✅ `requirements.txt` - зависимости Python
- ✅ `DEPLOYMENT.md` - инструкции по развертыванию
- ✅ `GIT_GUIDE.md` - руководство по Git
- ✅ `QUICK_START.md` - этот файл

## 🎉 Поздравляем!

Ваш проект готов для GitHub! Теперь вы можете:
- Поделиться кодом с другими
- Отслеживать изменения
- Работать в команде
- Развернуть на сервере
