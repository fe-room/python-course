"""
Day 66 — Offset / Limit 分页
=============================
演示后端分页的标准实现：
  - 使用 SQLAlchemy 的 .offset() / .limit() 方法
  - 返回 total_count（总条数） + items（当前页数据）
  - 客户端通过查询参数 ?page=1&size=20 控制

为什么需要分页？
  - 一次返回上万条数据会占用大量内存和带宽
  - 客户端渲染大量 DOM 节点会导致页面卡顿

运行方式:
    uvicorn day66_pagination:app --reload
"""

from __future__ import annotations

import logging
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean, func
from sqlalchemy.orm import (
    Session,
    declarative_base,
    sessionmaker,
)

# ---------------------------------------------------------------------------
# 数据库初始化
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
# Schema
# ---------------------------------------------------------------------------
class TodoOut(BaseModel):
    id: int
    title: str
    description: str
    done: bool

    model_config = ConfigDict(from_attributes=True)


class PaginatedTodoOut(BaseModel):
    """
    分页响应体：包含当前页数据和总条数。

    前端可以根据 total_count 计算总页数，渲染分页按钮。
    """

    items: List[TodoOut]
    total_count: int


# ---------------------------------------------------------------------------
# 依赖
# ---------------------------------------------------------------------------
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="Day 66 — 分页", version="0.1.0")

# 种子数据：启动时插入一些测试数据（如果表是空的）
SAMPLE_TODOS = [
    "学习 FastAPI",
    "学习 SQLAlchemy",
    "写 Repository 模式代码",
    "实现分页功能",
    "学习 pytest 测试",
    "部署到服务器",
    "配置 CI/CD",
    "写项目文档",
    "代码审查",
    "性能优化",
]


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    # 如果表为空，插入示例数据
    db = SessionLocal()
    try:
        if db.query(Todo).count() == 0:
            for title in SAMPLE_TODOS:
                db.add(Todo(title=title))
            db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Day 66 — Offset / Limit 分页"}


@app.get("/todos", response_model=PaginatedTodoOut)
def list_todos_paginated(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    size: int = Query(5, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    """
    分页获取 Todo 列表。

    查询参数：
      - page: 页码（默认 1）
      - size: 每页条数（默认 5，最大 100）

    返回：
      - items:      当前页的数据列表
      - total_count: 数据库中符合条件的总条数

    分页计算：
      offset = (page - 1) * size
    """
    # 先查总数（单独发一条 COUNT 查询）
    total_count = db.query(func.count(Todo.id)).scalar()

    # 再查当前页数据
    offset = (page - 1) * size
    items = (
        db.query(Todo)
        .order_by(Todo.id)       # 稳定的排序保证分页结果一致
        .offset(offset)
        .limit(size)
        .all()
    )

    return PaginatedTodoOut(items=items, total_count=total_count)


# ---------------------------------------------------------------------------
# 补充：基于 cursor 的游标分页（仅供扩展参考）
# ---------------------------------------------------------------------------
class CursorPageOut(BaseModel):
    """游标分页响应（非核心内容，仅展示思路）"""
    items: List[TodoOut]
    next_cursor: Optional[int] = None
    has_more: bool = False


@app.get("/todos/cursor", response_model=CursorPageOut)
def list_todos_cursor(
    cursor: Optional[int] = Query(None, description="上一页最后一条的 ID"),
    size: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    游标分页（Cursor-based Pagination）。
    适合无限滚动场景，性能优于 offset 分页。

    原理：
      - 客户端传上一页最后一条记录的 ID 作为 cursor
      - 服务端返回 id > cursor 的 N 条记录
      - 不需要 COUNT，在大表上性能更好
    """
    query = db.query(Todo).order_by(Todo.id).limit(size + 1)

    if cursor is not None:
        query = query.filter(Todo.id > cursor)

    results = query.all()

    # 多取一条来判断是否还有下一页
    has_more = len(results) > size
    items = results[:size]

    next_cursor = items[-1].id if items else None

    return CursorPageOut(items=items, next_cursor=next_cursor, has_more=has_more)


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("day66_pagination:app", host="127.0.0.1", port=8000, reload=True)