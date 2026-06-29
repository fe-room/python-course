"""
Day 64 — FastAPI + SQLAlchemy 集成
====================================
演示 FastAPI 与 SQLAlchemy 的标准整合方式：
  - SQLAlchemy ORM 模型定义
  - get_db 依赖注入
  - Pydantic response_model 数据脱敏
  - Create / List 两个基础端点

运行方式:
    uvicorn day64_fastapi_db:app --reload
"""

from __future__ import annotations

import logging
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import (
    Session,
    declarative_base,
    sessionmaker,
)

# ---------------------------------------------------------------------------
# 1. 数据库引擎 & Session 工厂
# ---------------------------------------------------------------------------
# SQLite 文件数据库，方便本地调试
DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 多线程支持
    echo=False,                                  # 生产环境建议关闭 SQL 日志
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------------------------
# 2. ORM 模型
# ---------------------------------------------------------------------------
Base = declarative_base()


class Todo(Base):
    """数据库中的 Todo 表"""

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), default="")
    done = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Todo(id={self.id}, title={self.title!r}, done={self.done})>"


# ---------------------------------------------------------------------------
# 3. Pydantic Schema（请求 / 响应）
# ---------------------------------------------------------------------------
class TodoCreate(BaseModel):
    """创建 Todo 时的请求体"""

    title: str
    description: str = ""
    done: bool = False


class TodoOut(BaseModel):
    """返回给客户端的数据模型 —— 脱敏、校验"""

    id: int
    title: str
    description: str
    done: bool

    # 允许从 ORM 对象直接转换
    model_config = ConfigDict(from_attributes=True)


class TodoUpdate(BaseModel):
    """更新 Todo 时的请求体（所有字段可选）"""

    title: Optional[str] = None
    description: Optional[str] = None
    done: Optional[bool] = None


# ---------------------------------------------------------------------------
# 4. 依赖注入 —— get_db
# ---------------------------------------------------------------------------
def get_db() -> Session:
    """FastAPI 依赖：在每个请求中创建新 Session，请求结束后关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 5. FastAPI 应用 & 端点
# ---------------------------------------------------------------------------
app = FastAPI(title="Day 64 — FastAPI + DB", version="0.1.0")


@app.on_event("startup")
def on_startup():
    """应用启动时自动建表"""
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Day 64 — FastAPI + SQLAlchemy 集成"}


# ── List Todos ──────────────────────────────────────────────────────
@app.get("/todos", response_model=List[TodoOut])
def list_todos(db: Session = Depends(get_db)):
    """获取所有 Todo 列表"""
    todos = db.query(Todo).all()
    return todos


# ── Get Single Todo ─────────────────────────────────────────────────
@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """根据 ID 获取单个 Todo"""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


# ── Create Todo ─────────────────────────────────────────────────────
@app.post("/todos", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    """创建一条新的 Todo"""
    todo = Todo(**payload.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo)  # 回填自增 ID
    return todo


# ── Update Todo ─────────────────────────────────────────────────────
@app.patch("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, payload: TodoUpdate, db: Session = Depends(get_db)):
    """局部更新 Todo 字段"""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    # 只更新传入了的字段
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)

    db.commit()
    db.refresh(todo)
    return todo


# ── Delete Todo ─────────────────────────────────────────────────────
@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """删除指定 Todo"""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()


# ---------------------------------------------------------------------------
# 6. 直接运行入口
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("day64_fastapi_db:app", host="127.0.0.1", port=8000, reload=True)