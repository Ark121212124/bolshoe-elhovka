Дипломный проект: сайт администрации + CRM-система обращений граждан
=====================================================================

Состав проекта
--------------
frontend/  — текущий сайт администрации Большеелховского сельского поселения.
backend/   — FastAPI backend API для приема обращений, загрузки фото, CRM и авторизации.
crm/       — интерфейс CRM-панели сотрудников, который открывается через backend по адресу /crm.

Что уже реализовано
-------------------
1. Помощник на сайте теперь пошагово собирает обращение:
   - ФИО;
   - телефон;
   - адрес/населенный пункт;
   - категорию;
   - тему;
   - текст обращения;
   - фотографию jpg/png/webp;
   - согласие на обработку персональных данных.

2. Обращение отправляется в backend API и сохраняется в базе данных.

3. Backend создает номер обращения вида BR-2026-00001.

4. Добавлена страница frontend/appeal-status.html для проверки статуса обращения.

5. CRM-панель позволяет сотруднику:
   - войти под логином admin / admin123, manager / manager123 или employee / employee123;
   - посмотреть список обращений;
   - открыть карточку обращения;
   - посмотреть фото;
   - изменить статус;
   - назначить ответственного;
   - добавить служебный или публичный комментарий.

6. Реализованы таблицы:
   - users;
   - appeal_categories;
   - appeals;
   - appeal_files;
   - appeal_comments;
   - appeal_history.

Быстрый локальный запуск на Windows
-----------------------------------
Самый простой вариант — запустить файл в корне проекта:

   start_project.bat

Он автоматически откроет backend, frontend, CRM-панель и документацию API.
Подробная инструкция находится в файле README_QUICK_START.txt.

Демо-входы в CRM:
- admin / admin123 — администратор;
- manager / manager123 — руководитель;
- employee / employee123 — сотрудник.

Локальный запуск backend вручную
--------------------------------
1. Откройте папку backend:

   cd backend

2. Создайте виртуальное окружение:

   python -m venv .venv

3. Активируйте окружение:

   Windows PowerShell:
   .venv\Scripts\Activate.ps1

   Windows CMD:
   .venv\Scripts\activate.bat

4. Установите зависимости:

   pip install -r requirements.txt

5. Запустите backend:

   uvicorn app.main:app --reload

6. Проверьте:

   http://localhost:8000/docs
   http://localhost:8000/crm

Локальный запуск frontend
-------------------------
Откройте файл frontend/index.html в браузере или запустите простой локальный сервер:

   cd frontend
   python -m http.server 5500

После этого сайт будет доступен по адресу:

   http://localhost:5500

По умолчанию frontend отправляет обращения на:

   http://localhost:8000

Если backend будет размещен на Render, замените адрес в файле:

   frontend/assets/js/appeals-config.js

На адрес backend-сервиса, например:

   window.APPEALS_API_URL = 'https://appeals-backend.onrender.com';
   window.CRM_PANEL_URL = 'https://appeals-backend.onrender.com/crm';

PostgreSQL
----------
Для локального дипломного показа можно использовать SQLite, он создается автоматически.
Для более правильной схемы с PostgreSQL запустите контейнер:

   docker compose up -d

И укажите переменную окружения:

   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/appeals_db

Размещение на Render
--------------------
Frontend:
- тип сервиса: Static Site;
- папка публикации: frontend или корень, если загрузить содержимое frontend отдельно.

Backend:
- тип сервиса: Web Service;
- Root Directory: backend;
- Build Command: pip install -r requirements.txt;
- Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT.

Переменные окружения backend на Render:
- DATABASE_URL — строка подключения PostgreSQL;
- SECRET_KEY — любая длинная секретная строка;
- CORS_ORIGINS — адрес frontend-сайта, например https://bolsheelxovskiy-syte.onrender.com;
- ADMIN_USERNAME — admin;
- ADMIN_PASSWORD — admin123 или другой пароль;
- ADMIN_FULL_NAME — Администратор системы.

Важно
-----
Это первая рабочая версия дипломного проекта. Она уже показывает архитектуру frontend + backend API + CRM + база данных.
Для промышленной эксплуатации дополнительно нужны: защищенная авторизация, резервное копирование, HTTPS, журналирование, регламент хранения персональных данных и полноценная серверная система хранения файлов.
