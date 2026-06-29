"""
Day 68 — N+1 查询问题 & selectinload 预加载
=============================================
什么是 N+1 问题？
  - 1 次查询获取 N 条主记录
  - 然后循环 N 次，每次查询关联表
  - 共执行 1 + N 次 SQL，性能灾难

解决方案：
  - selectinload()：预加载关联数据，只发 1 条额外查询
  - joinedload()：用 JOIN 一次性查出（适合一对一）
  - subqueryload()：子查询方式加载

运行方式:
    uvicorn day68_eager_load:app --reload
"""

from __future__ import annotations

import logging
import time
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import (
    Session,
    declarative_base,
    relationship,
    sessionmaker,
    selectinload,
    joinedload,
)

# ---------------------------------------------------------------------------
# 数据库初始化
# ---------------------------------------------------------------------------
DATABASE_URL = "sqlite:///./todos_relations.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # 建议临时设为 True 观察 SQL 执行情况
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ===================================================================
# 模型 —— 一对多关系
# ===================================================================
class User(Base):
    """用户表 —— 为了演示关系，一个用户可以拥有多个 Todo"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), default="")

    # ORM 关系：一个 User 有多个 Todo
    # back_populates 让两边互相感知，保持同步
    todos = relationship("Todo", back_populates="owner")


class Todo(Base):
    """Todo 表 —— 通过 user_id 关联到 User"""

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    done = Column(Boolean, default=False)

    # 外键 —— 这是数据库层面的约束
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ORM 关系：每个 Todo 属于一个 User
    # 反向引用到 User.todos
    owner = relationship("User", back_populates="todos")


# ===================================================================
# Schema
# ===================================================================
class UserOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class TodoOut(BaseModel):
    id: int
    title: str
    done: bool
    user_id: int
    owner: Optional[UserOut] = None  # 嵌套关系

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# 依赖
# ===================================================================
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===================================================================
# App
# ===================================================================
app = FastAPI(title="Day 68 — N+1 与 selectinload", version="0.1.0")


@app.on_event("startup")
def on_startup():
    """建表 + 种子数据"""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            # 创建 3 个用户，每个用户有 5 条 Todo
            for i in range(1, 4):
                user = User(name=f"用户{i}", email=f"user{i}@example.com")
                db.add(user)
                db.flush()  # 获取 user.id

                for j in range(1, 6):
                    db.add(
                        Todo(
                            title=f"用户{i} 的任务{j}",
                            done=(j % 2 == 0),
                            user_id=user.id,
                        )
                    )
            db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Day 68 — N+1 问题与 selectinload 预加载"}


# ===================================================================
# 问题演示：N+1
# ===================================================================
@app.get("/todos/n-plus-1", response_model=List[TodoOut])
def list_todos_n_plus_1(db: Session = Depends(get_db)):
    """
    【问题演示】N+1 查询。

    第一步：SELECT * FROM todos             -> 1 次查询，返回 N 条 Todo
    第二步：循环 N 次，每次 SELECT * FROM users WHERE id = ?
       -> N 次额外查询

    总计：1 + N 次 SQL 查询。

    当 N=100 时，需要 101 次数据库查询。
    当 N=10000 时，需要 10001 次 —— 直接拖垮数据库。
    """
    start = time.time()

    # 1 次查询
    todos = db.query(Todo).all()

    # N 次查询 —— 访问 .owner 时 SQLAlchemy 会懒加载
    for todo in todos:
        _ = todo.owner  # 每次触发一条 SELECT

    elapsed = time.time() - start
    logging.warning(f"[N+1] 查询耗时: {elapsed:.4f}s，共 {1 + len(todos)} 次 SQL")

    return todos


# ===================================================================
# 解决方案：selectinload
# ===================================================================
@app.get("/todos/eager", response_model=List[TodoOut])
def list_todos_eager(db: Session = Depends(get_db)):
    """
    【解决方案】使用 selectinload 预加载关联。

    selectinload 会在主查询之后额外发一条查询：
      SELECT * FROM users WHERE id IN (所有的 user_id)

    总计：2 次查询（无论 N 有多大）。

    适用场景：一对多、多对多关系。
    """
    start = time.time()

    # 使用 selectinload 提前加载 owner 关系
    todos = db.query(Todo).options(
        selectinload(Todo.owner)  # 预加载，只多发 1~2 条 SQL
    ).all()

    for todo in todos:
        _ = todo.owner  # 此时 owner 已加载，不再发 SQL

    elapsed = time.time() - start
    logging.warning(f"[Eager] 查询耗时: {elapsed:.4f}s，共 2 次 SQL")

    return todos


# ===================================================================
# 补充：joinedload
# ===================================================================
@app.get("/todos/joined", response_model=List[TodoOut])
def list_todos_joined(db: Session = Depends(get_db)):
    """
    另一种预加载方式：joinedload。

    使用 LEFT JOIN 一次性查出所有数据：
      SELECT todos.*, users.* FROM todos LEFT JOIN users ON ...

    优势：只需要 1 次查询。
    劣势：
      - 如果关联表很大，JOIN 可能很慢
      - 如果主表有多条记录关联同一条副表记录，会产生重复数据

    适用场景：一对一、多对一关系。
    """
    start = time.time()

    todos = db.query(Todo).options(
        joinedload(Todo.owner)  # 使用 JOIN 预加载
    ).all()

    for todo in todos:
        _ = todo.owner

    elapsed = time.time() - start
    logging.warning(f"[Joined] 查询耗时: {elapsed:.4f}s，共 1 次 SQL")

    return todos


# ===================================================================
# 反向预加载：从 User 加载 Todo
# ===================================================================
@app.get("/users/{user_id}/todos", response_model=List[TodoOut])
def get_user_todos(user_id: int, db: Session = Depends(get_db)):
    """
    获取指定用户的所有 Todo，同时预加载 owner 信息。

    注意：这里 user_id 是明确的，不是 N+1 问题场景，
    但同样可以通过 selectinload 避免后续访问 owner 时重复查询。
    """
    todos = (
        db.query(Todo)
        .options(selectinload(Todo.owner))
        .filter(Todo.user_id == user_id)
        .all()
    )
    return todos


# ===================================================================
# 选择指南
# ===================================================================
"""
预加载策略选择：

| 场景            | 推荐策略        | 说明                                |
|----------------|----------------|-------------------------------------|
| 一对多 / 多对多  | selectinload   | 多发一条 WHERE IN 查询，数据量大时友好 |
| 多对一 / 一对一  | joinedload     | 用 JOIN 合并查询，减少查询次数         |
| 不确定 / 默认    | selectinload   | 大多数场景表现稳定                    |

注意事项：
  1. 不要同时对一个关系使用多个 loading 策略
  2. 如果不需要关联数据，什么都别加 —— 懒加载就是最佳方案
  3. 在序列化（.json() / model_dump()）时，SQLAlchemy 会
     自动触发尚未加载的关系，注意不要因此踩 N+1 的坑
"""

# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("day68_eager_load:app", host="127.0.0.1", port=8000, reload=True)