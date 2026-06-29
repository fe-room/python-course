"""
Day 67 — 多条件过滤查询
=========================
演示 SQLAlchemy 中常见的过滤场景：
  - 关键词搜索（.contains()）
  - 按 done 状态过滤
  - 多条件组合（and_ / or_）
  - 动态构建查询（根据用户传入的参数灵活拼接 .filter()）

运行方式:
    uvicorn day67_filter:app --reload
"""

from __future__ import annotations

import logging
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean, or_
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
app = FastAPI(title="Day 67 — 多条件过滤", version="0.1.0")


@app.on_event("startup")
def on_startup():
    """启动时建表 + 插入种子数据"""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Todo).count() == 0:
            seeds = [
                Todo(title="买苹果", description="去超市买一箱红富士"),
                Todo(title="学 FastAPI", description="看完官方教程的前五章"),
                Todo(title="修电脑", description="换个固态硬盘"),
                Todo(title="写周报", description="本周完成内容汇总"),
                Todo(title="去健身房", description="跑步 30 分钟 + 力量训练"),
                Todo(title="买水果", description="香蕉和橙子各买一些"),
            ]
            db.add_all(seeds)
            db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Day 67 — 多条件过滤查询"}


# ===================================================================
# 核心：多条件过滤端点
# ===================================================================
@app.get("/todos", response_model=List[TodoOut])
def filter_todos(
    # ── 关键词搜索（可选） ────────────────────────────────────────
    keyword: Optional[str] = Query(
        None,
        min_length=1,
        description="搜索关键词，匹配 title 或 description 字段",
    ),
    # ── 完成状态过滤（可选） ──────────────────────────────────────
    done: Optional[bool] = Query(
        None,
        description="按完成状态过滤：true / false / 不传表示不限",
    ),
    db: Session = Depends(get_db),
):
    """
    多条件过滤 Todo 列表。

    特性说明：
      1. keyword 使用 contains() → 相当于 SQL 的 LIKE '%keyword%'
      2. done 使用精确匹配
      3. 两个条件都是可选的，不传就不加对应过滤
      4. 如果都不传，则返回全部数据

    SQLAlchemy 的 .filter() 可以多次调用，每次调用相当于
    在前面的基础上加 AND 条件。
    """
    # 1. 构建基础查询
    query = db.query(Todo)

    # 2. 动态拼接条件
    #    如果 keyword 不为空，在 title 和 description 中模糊搜索
    if keyword:
        query = query.filter(
            or_(
                Todo.title.contains(keyword),
                Todo.description.contains(keyword),
            )
        )
        # 说明：contains() 在 SQLite/PostgreSQL/MySQL 中会生成 LIKE 语句
        #       SQLite 默认不区分大小写，PostgreSQL 区分，需要注意
        #
        # 如果需要大小写不敏感的搜索，可以用：
        #   Todo.title.ilike(f"%{keyword}%")

    # 3. 如果 done 状态有指定，精确过滤
    if done is not None:
        query = query.filter(Todo.done == done)

    # 4. 按 ID 排序后返回
    return query.order_by(Todo.id).all()


# ===================================================================
# 补充：更灵活的搜索（演示 SQLAlchemy 多个过滤方式）
# ===================================================================
@app.get("/todos/search", response_model=List[TodoOut])
def search_todos_advanced(
    q: Optional[str] = Query(None, description="全局搜索（匹配 title 或 description）"),
    title: Optional[str] = Query(None, description="精确搜索标题"),
    done: Optional[bool] = Query(None, description="完成状态"),
    min_id: Optional[int] = Query(None, ge=1, description="最小 ID"),
    max_id: Optional[int] = Query(None, ge=1, description="最大 ID"),
    db: Session = Depends(get_db),
):
    """
    高级搜索 —— 展示 .contains / .like / 比较运算符 等多种过滤方式。

    SQLAlchemy 常用过滤操作符：
      - .contains(value)       → LIKE '%value%'
      - .startswith(value)     → LIKE 'value%'
      - .endswith(value)       → LIKE '%value'
      - .like(pattern)         → 自定义 LIKE 模式
      - .in_([a, b, c])        → IN 查询
      - column > value         → 大于
      - column >= value        → 大于等于
      - column < value         → 小于
      - column.between(a, b)   → BETWEEN
      - column.is_(None)       → IS NULL
    """
    query = db.query(Todo)

    if q:
        query = query.filter(
            or_(
                Todo.title.contains(q),
                Todo.description.contains(q),
            )
        )

    if title:
        query = query.filter(Todo.title == title)

    if done is not None:
        query = query.filter(Todo.done == done)

    if min_id is not None:
        query = query.filter(Todo.id >= min_id)

    if max_id is not None:
        query = query.filter(Todo.id <= max_id)

    return query.order_by(Todo.id).all()


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("day67_filter:app", host="127.0.0.1", port=8000, reload=True)