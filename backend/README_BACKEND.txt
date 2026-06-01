Backend API дипломного проекта
==============================

Команды запуска:
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload

Адреса:
http://localhost:8000/docs — документация API
http://localhost:8000/crm — CRM-панель

Демо-входы:
admin / admin123 — администратор
manager / manager123 — руководитель
employee / employee123 — сотрудник

PRODUCTION / RENDER
-------------------
Для Render используйте:
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Root Directory: backend

Backend читает DATABASE_URL из переменных окружения. Если DATABASE_URL начинается с postgres://,
код автоматически преобразует его в postgresql:// для SQLAlchemy.
