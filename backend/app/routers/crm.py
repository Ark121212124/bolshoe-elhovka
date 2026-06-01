from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query, status
from ..database import get_db
from ..deps import get_current_user, require_manager
from ..models import Appeal, AppealComment, AppealFile, AppealHistory, User
from ..schemas import (
    AppealDetailOut,
    AppealListOut,
    AssignIn,
    CommentIn,
    StatusUpdateIn,
    UserCreateIn,
    UserOut,
)
from ..security import hash_password

router = APIRouter(prefix="/api/crm", tags=["CRM"])

STATUSES = ["Новое", "Принято", "Назначено", "В работе", "Требуется уточнение", "Выполнено", "Закрыто", "Отклонено"]


def file_to_out(file: AppealFile) -> dict:
    return {
        "id": file.id,
        "file_name": file.file_name,
        "file_path": file.file_path,
        "url": f"/uploads/{file.file_path}",
        "content_type": file.content_type,
    }


def appeal_to_list(item: Appeal) -> AppealListOut:
    return AppealListOut(
        id=item.id,
        number=item.number or "",
        citizen_full_name=item.citizen_full_name,
        citizen_phone=item.citizen_phone,
        citizen_address=item.citizen_address,
        title=item.title,
        status=item.status,
        category=item.category.name if item.category else None,
        assigned_to=item.assigned_user.full_name if item.assigned_user else None,
        created_at=item.created_at,
        updated_at=item.updated_at,
        file_count=len(item.files),
    )


def appeal_to_detail(item: Appeal) -> AppealDetailOut:
    base = appeal_to_list(item).model_dump()
    base.update({
        "text": item.text,
        "consent_personal_data": item.consent_personal_data,
        "files": [file_to_out(f) for f in item.files],
        "comments": [
            {
                "id": c.id,
                "comment": c.comment,
                "is_public": c.is_public,
                "author": c.user.full_name if c.user else None,
                "created_at": c.created_at,
            }
            for c in item.comments
        ],
        "history": [
            {
                "id": h.id,
                "action": h.action,
                "old_value": h.old_value,
                "new_value": h.new_value,
                "created_at": h.created_at.isoformat(),
            }
            for h in item.history
        ],
    })
    return AppealDetailOut(**base)


@router.get("/statuses")
def statuses(user: User = Depends(get_current_user)):
    return STATUSES


@router.get("/stats")
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Appeal.status, func.count(Appeal.id)).group_by(Appeal.status).all()
    total = db.query(func.count(Appeal.id)).scalar() or 0
    return {"total": total, "by_status": {status: count for status, count in rows}}


@router.get("/users", response_model=list[UserOut])
def users(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(User).filter(User.is_active == True).order_by(User.full_name.asc()).all()


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreateIn, db: Session = Depends(get_db), user: User = Depends(require_manager)):
    exists = db.query(User).filter(User.username == data.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")
    new_user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        phone=data.phone,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/appeals", response_model=list[AppealListOut])
def appeals(
    status_value: str | None = Query(default=None, alias="status"),
    q: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Appeal).order_by(Appeal.created_at.desc())
    if user.role == "employee":
        query = query.filter(or_(Appeal.assigned_to_id == user.id, Appeal.assigned_to_id.is_(None)))
    if status_value:
        query = query.filter(Appeal.status == status_value)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(or_(Appeal.number.ilike(term), Appeal.title.ilike(term), Appeal.citizen_full_name.ilike(term), Appeal.citizen_phone.ilike(term)))
    return [appeal_to_list(item) for item in query.limit(250).all()]


@router.get("/appeals/{appeal_id}", response_model=AppealDetailOut)
def appeal_detail(appeal_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.get(Appeal, appeal_id)
    if not item:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    if user.role == "employee" and item.assigned_to_id not in {None, user.id}:
        raise HTTPException(status_code=403, detail="Нет доступа к обращению")
    return appeal_to_detail(item)


@router.patch("/appeals/{appeal_id}/status", response_model=AppealDetailOut)
def update_status(appeal_id: int, data: StatusUpdateIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if data.status not in STATUSES:
        raise HTTPException(status_code=400, detail="Неизвестный статус")
    item = db.get(Appeal, appeal_id)
    if not item:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    old = item.status
    item.status = data.status
    db.add(AppealHistory(appeal=item, user_id=user.id, action="Изменен статус", old_value=old, new_value=data.status))
    db.commit()
    db.refresh(item)
    return appeal_to_detail(item)


@router.patch("/appeals/{appeal_id}/assign", response_model=AppealDetailOut)
def assign(appeal_id: int, data: AssignIn, db: Session = Depends(get_db), user: User = Depends(require_manager)):
    item = db.get(Appeal, appeal_id)
    if not item:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    assigned = db.get(User, data.user_id) if data.user_id else None
    old = item.assigned_user.full_name if item.assigned_user else "Не назначен"
    item.assigned_to_id = assigned.id if assigned else None
    if item.status == "Новое" and assigned:
        item.status = "Назначено"
    db.add(AppealHistory(appeal=item, user_id=user.id, action="Назначен ответственный", old_value=old, new_value=assigned.full_name if assigned else "Не назначен"))
    db.commit()
    db.refresh(item)
    return appeal_to_detail(item)


@router.post("/appeals/{appeal_id}/comments", response_model=AppealDetailOut)
def add_comment(appeal_id: int, data: CommentIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.get(Appeal, appeal_id)
    if not item:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    if not data.comment.strip():
        raise HTTPException(status_code=400, detail="Комментарий пустой")
    db.add(AppealComment(appeal=item, user_id=user.id, comment=data.comment.strip(), is_public=data.is_public))
    db.add(AppealHistory(appeal=item, user_id=user.id, action="Добавлен комментарий", new_value="Публичный" if data.is_public else "Служебный"))
    db.commit()
    db.refresh(item)
    return appeal_to_detail(item)
