ГОТОВАЯ ВЕРСИЯ ДЛЯ GITHUB + RENDER
===================================

Проект состоит из трех частей:

1) frontend/ — сайт администрации, размещается как Render Static Site.
2) backend/ — FastAPI backend API, размещается как Render Web Service.
3) PostgreSQL — база данных на Render для обращений, сотрудников, статусов, истории и комментариев.

ВАЖНО
-----
Фотографии сайта не изменялись. Они остаются в frontend/assets/img/.
Фотографии обращений пользователей сохраняются backend-сервисом в backend/uploads/.

ЛОКАЛЬНАЯ ПРОВЕРКА
------------------
1. Распакуйте архив.
2. Запустите start_project.bat.
3. Откройте:
   сайт: http://127.0.0.1:5500
   CRM:  http://127.0.0.1:8000/crm
   API:  http://127.0.0.1:8000/docs

Демо-вход в CRM:
   admin / admin123
   manager / manager123
   employee / employee123

ЗАГРУЗКА НА GITHUB
------------------
1. Создайте новый репозиторий на GitHub.
2. Загрузите ВЕСЬ проект целиком, не только frontend.
   В корне репозитория должны лежать:
   - frontend/
   - backend/
   - crm/
   - render.yaml
   - docker-compose.yml
   - README_DEPLOY_RENDER_GITHUB.txt

3. Не загружайте локальные временные файлы:
   - backend/.venv/
   - backend/appeals.db
   - backend/uploads/
   Они уже добавлены в .gitignore.

АВТОМАТИЧЕСКИЙ ДЕПЛОЙ НА RENDER ЧЕРЕЗ render.yaml
-------------------------------------------------
1. Откройте Render.com.
2. Нажмите New +.
3. Выберите Blueprint.
4. Подключите GitHub-репозиторий с проектом.
5. Render увидит файл render.yaml и предложит создать:
   - bolsheelxovskiy-appeals-api
   - bolsheelxovskiy-appeals-site
   - bolsheelxovskiy-appeals-db
6. Подтвердите создание сервисов.

После деплоя будут адреса примерно такого вида:
   Frontend: https://bolsheelxovskiy-appeals-site.onrender.com
   Backend:  https://bolsheelxovskiy-appeals-api.onrender.com
   CRM:      https://bolsheelxovskiy-appeals-api.onrender.com/crm
   API Docs: https://bolsheelxovskiy-appeals-api.onrender.com/docs

ЕСЛИ BACKEND НА RENDER ПОЛУЧИЛ ДРУГОЙ АДРЕС
-------------------------------------------
Откройте файл:
   frontend/assets/js/appeals-config.js

Найдите строку:
   const PRODUCTION_API = 'https://bolsheelxovskiy-appeals-api.onrender.com';

Замените адрес на фактический адрес backend-сервиса Render.
После этого сделайте commit/push в GitHub, Render сам обновит сайт.

НАСТРОЙКИ BACKEND НА RENDER ВРУЧНУЮ
-----------------------------------
Если создаете backend не через Blueprint, а вручную:

Service type: Web Service
Runtime: Python
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

Environment variables:
DATABASE_URL = строка подключения PostgreSQL
SECRET_KEY = любая длинная случайная строка
CORS_ORIGINS = https://АДРЕС-САЙТА.onrender.com,http://localhost:5500,http://127.0.0.1:5500
ADMIN_USERNAME = admin
ADMIN_PASSWORD = admin123

НАСТРОЙКИ FRONTEND НА RENDER ВРУЧНУЮ
------------------------------------
Если создаете сайт не через Blueprint, а вручную:

Service type: Static Site
Root Directory: frontend
Build Command: оставить пустым
Publish Directory: .

ПРОВЕРКА ПОСЛЕ ДЕПЛОЯ
---------------------
1. Откройте backend /docs:
   https://ВАШ-BACKEND.onrender.com/docs
   Если открылась документация FastAPI — backend работает.

2. Откройте CRM:
   https://ВАШ-BACKEND.onrender.com/crm
   Войдите admin / admin123.

3. Откройте frontend-сайт.
   Через помощника создайте обращение.

4. Вернитесь в CRM.
   Обращение должно появиться в списке.

5. В CRM измените статус обращения.
   На сайте откройте страницу проверки статуса и проверьте номер обращения.

ПРИМЕЧАНИЕ ПРО ФОТО ОБРАЩЕНИЙ
-----------------------------
В проекте предусмотрена загрузка фотографий к обращениям. Для дипломной версии используется серверная папка backend/uploads/.
В render.yaml добавлен disk appeals-uploads, чтобы файлы не пропадали после перезапуска сервиса.
В промышленной версии можно заменить это на S3-совместимое облачное хранилище.
