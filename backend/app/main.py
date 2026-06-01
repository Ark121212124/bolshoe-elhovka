from pathlib import Path
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .models import AppealCategory, User
from .security import hash_password
from .routers import auth, public, crm

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = Path(__file__).resolve().parents[2]
UPLOADS_DIR = Path(os.getenv("UPLOADS_DIR", str(BASE_DIR / "uploads")))
CRM_DIR = Path(os.getenv("CRM_DIR", str(PROJECT_DIR / "crm")))
if not CRM_DIR.exists():
    CRM_DIR = BASE_DIR / "crm"

app = FastAPI(
    title="CRM-система обработки обращений граждан",
    description="Backend API для сайта администрации Большеелховского сельского поселения",
    version="1.0.0",
)

origins_raw = os.getenv("CORS_ORIGINS", "*")
origins = [item.strip() for item in origins_raw.split(",") if item.strip()] or ["*"]
allow_all_origins = origins == ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
if (CRM_DIR / "assets").exists():
    app.mount("/crm-assets", StaticFiles(directory=str(CRM_DIR / "assets")), name="crm_assets")

app.include_router(public.router)
app.include_router(auth.router)
app.include_router(crm.router)


def seed_data():
    db: Session = SessionLocal()
    try:
        categories = [
            "ЖКХ и благоустройство",
            "Дороги и транспорт",
            "Безопасность",
            "Земельные вопросы",
            "Социальная сфера",
            "Образование и культура",
            "Другое",
        ]
        for name in categories:
            if not db.query(AppealCategory).filter(AppealCategory.name == name).first():
                db.add(AppealCategory(name=name))
        demo_users = [
            {
                "username": os.getenv("ADMIN_USERNAME", "admin"),
                "password": os.getenv("ADMIN_PASSWORD", "admin123"),
                "full_name": os.getenv("ADMIN_FULL_NAME", "Администратор системы"),
                "role": "admin",
                "phone": None,
            },
            {
                "username": os.getenv("MANAGER_USERNAME", "manager"),
                "password": os.getenv("MANAGER_PASSWORD", "manager123"),
                "full_name": os.getenv("MANAGER_FULL_NAME", "Руководитель администрации"),
                "role": "manager",
                "phone": "+7 (83441) 3-09-90",
            },
            {
                "username": os.getenv("EMPLOYEE_USERNAME", "employee"),
                "password": os.getenv("EMPLOYEE_PASSWORD", "employee123"),
                "full_name": os.getenv("EMPLOYEE_FULL_NAME", "Сотрудник администрации"),
                "role": "employee",
                "phone": "+7 (83441) 3-09-90",
            },
        ]
        for item in demo_users:
            if not db.query(User).filter(User.username == item["username"]).first():
                db.add(User(
                    username=item["username"],
                    password_hash=hash_password(item["password"]),
                    full_name=item["full_name"],
                    role=item["role"],
                    phone=item["phone"],
                ))
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed_data()


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <h1>CRM API работает</h1>
    <p>Документация API: <a href='/docs'>/docs</a></p>
    <p>CRM-панель: <a href='/crm'>/crm</a></p>
    """


@app.get("/crm", response_class=HTMLResponse)
def crm_index():
    index_file = CRM_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("CRM-файлы не найдены", status_code=404)
