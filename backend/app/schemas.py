from datetime import datetime
from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: str

    model_config = {"from_attributes": True}


class LoginIn(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class FileOut(BaseModel):
    id: int
    file_name: str
    file_path: str
    url: str
    content_type: str | None = None


class CommentIn(BaseModel):
    comment: str
    is_public: bool = False


class CommentOut(BaseModel):
    id: int
    comment: str
    is_public: bool
    author: str | None
    created_at: datetime


class AppealListOut(BaseModel):
    id: int
    number: str
    citizen_full_name: str
    citizen_phone: str
    citizen_address: str | None
    title: str
    status: str
    category: str | None
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime
    file_count: int


class AppealDetailOut(AppealListOut):
    text: str
    consent_personal_data: bool
    files: list[FileOut]
    comments: list[CommentOut]
    history: list[dict]


class StatusUpdateIn(BaseModel):
    status: str


class AssignIn(BaseModel):
    user_id: int | None


class UserCreateIn(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "employee"
    phone: str | None = None
