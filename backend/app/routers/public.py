from datetime import datetime
from pathlib import Path
from uuid import uuid4
import re
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Appeal, AppealCategory, AppealFile, AppealHistory
from ..schemas import CategoryOut

router = APIRouter(prefix="/api", tags=["Публичная часть"])
import os
UPLOADS_DIR = Path(os.getenv("UPLOADS_DIR", str(Path(__file__).resolve().parents[2] / "uploads")))
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def normalize_phone(value: str) -> str:
    return re.sub(r"\D+", "", value or "")


def get_or_create_category(db: Session, category_name: str | None) -> AppealCategory | None:
    name = (category_name or "Прочее").strip() or "Прочее"
    category = db.query(AppealCategory).filter(AppealCategory.name == name).first()
    if not category:
        category = AppealCategory(name=name)
        db.add(category)
        db.flush()
    return category


@router.get("/health")
def health():
    return {"status": "ok", "service": "appeals-crm-api"}


@router.get("/categories", response_model=list[CategoryOut])
def categories(db: Session = Depends(get_db)):
    return db.query(AppealCategory).order_by(AppealCategory.name.asc()).all()


@router.post("/appeals", status_code=status.HTTP_201_CREATED)
def create_appeal(
    citizen_full_name: str = Form(...),
    citizen_phone: str = Form(...),
    citizen_address: str = Form(""),
    category_name: str = Form("Прочее"),
    title: str = Form(...),
    text: str = Form(...),
    consent_personal_data: bool = Form(False),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    if not consent_personal_data:
        raise HTTPException(status_code=400, detail="Необходимо согласие на обработку персональных данных")
    if len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Текст обращения слишком короткий")
    category = get_or_create_category(db, category_name)
    appeal = Appeal(
        citizen_full_name=citizen_full_name.strip(),
        citizen_phone=citizen_phone.strip(),
        citizen_address=citizen_address.strip() or None,
        category=category,
        title=title.strip(),
        text=text.strip(),
        consent_personal_data=consent_personal_data,
        status="Новое",
    )
    db.add(appeal)
    db.flush()
    appeal.number = f"BR-{datetime.now().year}-{appeal.id:05d}"

    if photo and photo.filename:
        ext = Path(photo.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Можно прикрепить только фото jpg, png или webp")
        target_dir = UPLOADS_DIR / "appeals" / appeal.number
        target_dir.mkdir(parents=True, exist_ok=True)
        safe_name = f"{uuid4().hex}{ext}"
        target = target_dir / safe_name
        data = photo.file.read()
        if len(data) > 8 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Фото не должно быть больше 8 МБ")
        target.write_bytes(data)
        db.add(AppealFile(
            appeal=appeal,
            file_name=photo.filename,
            file_path=f"appeals/{appeal.number}/{safe_name}",
            content_type=photo.content_type,
        ))

    db.add(AppealHistory(appeal=appeal, action="Обращение создано", new_value="Новое"))
    db.commit()
    db.refresh(appeal)
    return {
        "id": appeal.id,
        "number": appeal.number,
        "status": appeal.status,
        "message": "Обращение зарегистрировано и передано в CRM-систему",
    }


@router.get("/appeals/status")
def get_status(
    number: str = Query(...),
    phone: str = Query(...),
    db: Session = Depends(get_db),
):
    appeal = db.query(Appeal).filter(Appeal.number == number.strip()).first()
    if not appeal or normalize_phone(appeal.citizen_phone)[-7:] != normalize_phone(phone)[-7:]:
        raise HTTPException(status_code=404, detail="Обращение не найдено. Проверьте номер и телефон")
    public_comments = [
        {"comment": c.comment, "created_at": c.created_at.isoformat()}
        for c in appeal.comments if c.is_public
    ]
    return {
        "number": appeal.number,
        "title": appeal.title,
        "category": appeal.category.name if appeal.category else None,
        "status": appeal.status,
        "created_at": appeal.created_at.isoformat(),
        "updated_at": appeal.updated_at.isoformat(),
        "comments": public_comments,
    }
