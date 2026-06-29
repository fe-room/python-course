"""
Day 65 — Repository 模式（仓储模式）
====================================
将数据库查询逻辑从路由中抽离到 Repository 类中，使代码更加可测试、可维护。

核心思想：
  - TodoRepository 封装所有 Todo 表的 CRUD 操作
  - 路由函数只管"HTTP 语义"，不管"SQL 语法"

注意：
  ----- 小项目不需要这一层，直接用 db.query 更简洁 -----
  当项目膨胀到 20+ 个表时，Repository 的优势才会显现。

运行方式:
    uvicorn day65_repository:app --reload
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
# 数据库初始化（复用 day64 的逻辑）
# ---------------------------------------------------------------------------
DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), default="")
    done = Column(Boolean, default=False)


# ---------------------------------------------------------------------------
# Pydantic Schema
# ---------------------------------------------------------------------------
class TodoCreate(BaseModel):
    title: str
    description: str = ""
    done: bool = False


class TodoOut(BaseModel):
    id: int
    title: str
    description: str
    done: bool

    model_config = ConfigDict(from_attributes=True)


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    done: Optional[bool] = None


# ---------------------------------------------------------------------------
# get_db 依赖
# ---------------------------------------------------------------------------
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===================================================================
# TodoRepository —— 仓储类
# ===================================================================
class TodoRepository:
    """
    封装对 Todo 表的所有数据库操作。

    优势：
      1. 路由代码变短，只关心 HTTP
      2. 单元测试时可以 mock repository
      3. 如果 ORM 切换（比如从 SQLAlchemy 换到 Django ORM），
         只需要修改这一个类
    """

    def __init__(self, db: Session):
        self.db = db

    # ── 查询全部 ──────────────────────────────────────────────────
    def get_all(self) -> List[Todo]:
        """返回所有 Todo 记录"""
        return self.db.query(Todo).all()

    # ── 根据 ID 查询 ───────────────────────────────────────────────
    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        """根据主键 ID 查找单条记录，不存在返回 None"""
        return self.db.query(Todo).filter(Todo.id == todo_id).first()

    # ── 创建 ──────────────────────────────────────────────────────
    def create(self, data: TodoCreate) -> Todo:
        """创建一条 Todo 并提交"""
        todo = Todo(**data.model_dump())
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    # ── 更新 ──────────────────────────────────────────────────────
    def update(self, todo: Todo, data: TodoUpdate) -> Todo:
        """对已存在的 Todo 对象做局部更新"""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    # ── 删除 ──────────────────────────────────────────────────────
    def delete(self, todo: Todo) -> None:
        """删除指定的 Todo 对象"""
        self.db.delete(todo)
        self.db.commit()


# ===================================================================
# FastAPI 路由 —— 通过 Repository 操作数据库
# ===================================================================
app = FastAPI(title="Day 65 — Repository 模式", version="0.1.0")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Day 65 — Repository 模式"}


# 每个路由都通过 Depends(get_db) 获取 Session，然后实例化 Repository
# 虽然每次都 new 一个对象，但开销极小，可以忽略不计


@app.get("/todos", response_model=List[TodoOut])
def list_todos(db: Session = Depends(get_db)):
    """使用 Repository 获取全部 Todo"""
    repo = TodoRepository(db)
    return repo.get_all()


@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """使用 Repository 获取单个 Todo"""
    repo = TodoRepository(db)
    todo = repo.get_by_id(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/todos", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    """使用 Repository 创建 Todo"""
    repo = TodoRepository(db)
    return repo.create(payload)


@app.patch("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, payload: TodoUpdate, db: Session = Depends(get_db)):
    """使用 Repository 更新 Todo"""
    repo = TodoRepository(db)
    todo = repo.get_by_id(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return repo.update(todo, payload)


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """使用 Repository 删除 Todo"""
    repo = TodoRepository(db)
    todo = repo.get_by_id(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    repo.delete(todo)


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("day65_repository:app", host="127.0.0.1", port=8000, reload=True)