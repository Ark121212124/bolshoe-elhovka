from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(40), default="employee", nullable=False)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

    assigned_appeals = relationship("Appeal", back_populates="assigned_user", foreign_keys="Appeal.assigned_to_id")
    comments = relationship("AppealComment", back_populates="user")


class AppealCategory(Base):
    __tablename__ = "appeal_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    appeals = relationship("Appeal", back_populates="category")


class Appeal(Base):
    __tablename__ = "appeals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    number: Mapped[str | None] = mapped_column(String(40), unique=True, index=True, nullable=True)
    citizen_full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    citizen_phone: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    citizen_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(60), default="Новое", index=True, nullable=False)
    consent_personal_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("appeal_categories.id"), nullable=True)
    assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)

    category = relationship("AppealCategory", back_populates="appeals")
    assigned_user = relationship("User", back_populates="assigned_appeals", foreign_keys=[assigned_to_id])
    files = relationship("AppealFile", back_populates="appeal", cascade="all, delete-orphan")
    comments = relationship("AppealComment", back_populates="appeal", cascade="all, delete-orphan")
    history = relationship("AppealHistory", back_populates="appeal", cascade="all, delete-orphan")


class AppealFile(Base):
    __tablename__ = "appeal_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    appeal_id: Mapped[int] = mapped_column(ForeignKey("appeals.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

    appeal = relationship("Appeal", back_populates="files")


class AppealComment(Base):
    __tablename__ = "appeal_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    appeal_id: Mapped[int] = mapped_column(ForeignKey("appeals.id"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

    appeal = relationship("Appeal", back_populates="comments")
    user = relationship("User", back_populates="comments")


class AppealHistory(Base):
    __tablename__ = "appeal_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    appeal_id: Mapped[int] = mapped_column(ForeignKey("appeals.id"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    old_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    new_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

    appeal = relationship("Appeal", back_populates="history")
