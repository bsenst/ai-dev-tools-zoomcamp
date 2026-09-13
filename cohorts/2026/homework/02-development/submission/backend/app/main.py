from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import DateTime, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class TaskRecord(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(500), default="")
    priority: Mapped[str] = mapped_column(String(10), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="todo")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")

    @field_validator("title")
    @classmethod
    def title_must_contain_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("title must contain text")
        return value.strip()


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    priority: str | None = Field(default=None, pattern="^(low|medium|high)$")
    status: str | None = Field(default=None, pattern="^(todo|in_progress|done)$")

    @field_validator("title")
    @classmethod
    def updated_title_must_contain_text(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("title must contain text")
        return value.strip() if value is not None else None


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    priority: str
    status: str
    created_at: datetime


def create_app(database_url: str | None = None) -> FastAPI:
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///./flowboard.db")
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args)
    sessions = sessionmaker(bind=engine, expire_on_commit=False)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        Base.metadata.create_all(engine)
        yield
        engine.dispose()

    application = FastAPI(title="Flowboard API", version="1.0.0", lifespan=lifespan)
    Base.metadata.create_all(engine)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def get_session() -> Generator[Session, None, None]:
        with sessions() as session:
            yield session

    def find_task(task_id: int, session: Session) -> TaskRecord:
        task = session.get(TaskRecord, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    @application.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/api/tasks", response_model=list[Task])
    def list_tasks(session: Session = Depends(get_session)) -> list[TaskRecord]:
        return list(session.scalars(select(TaskRecord).order_by(TaskRecord.created_at.desc())))

    @application.post("/api/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
    def create_task(payload: TaskCreate, session: Session = Depends(get_session)) -> TaskRecord:
        task = TaskRecord(**payload.model_dump(), status="todo")
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @application.patch("/api/tasks/{task_id}", response_model=Task)
    def update_task(task_id: int, payload: TaskUpdate, session: Session = Depends(get_session)) -> TaskRecord:
        task = find_task(task_id, session)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        session.commit()
        session.refresh(task)
        return task

    @application.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_task(task_id: int, session: Session = Depends(get_session)) -> Response:
        task = find_task(task_id, session)
        session.delete(task)
        session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return application


app = create_app()