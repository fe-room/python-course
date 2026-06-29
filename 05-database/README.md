# 第五阶段：数据库（第 9-10 周）

难度：★★★★☆ | 前置：第四阶段 FastAPI

## 目录

```
05-database/
├── README.md
├── week9-sql/code/
│   ├── day57_sqlite_basics.py
│   ├── day58_sql_joins.py
│   ├── day59_sqlalchemy_intro.py
│   ├── day60_sqlalchemy_crud.py
│   ├── day61_relationships.py
│   ├── day62_alembic.py
│   └── day63_sqlite_todo.py
├── week10-fastapi-db/code/
│   ├── day64_fastapi_db.py
│   ├── day65_repository.py
│   ├── day66_pagination.py
│   ├── day67_filter.py
│   ├── day68_eager_load.py
│   └── day69_settings.py
└── project-todo-db/
    └── app/
        ├── main.py
        ├── database.py
        ├── models.py
        ├── schemas.py
        ├── crud.py
        └── requirements.txt
```

## 第 9 周：SQL + SQLAlchemy

### Day 57 — SQLite 基础

```python
# day57_sqlite_basics.py
import sqlite3

conn = sqlite3.connect("app.db")
cur = conn.cursor()

# 建表
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 插入
cur.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@x.com"))
conn.commit()

# 查询
cur.execute("SELECT * FROM users")
rows = cur.fetchall()
for row in rows:
    print(row)

conn.close()
```

**注意**：SQLite 的 `?` 占位符（不是 f-string），防 SQL 注入

---

### Day 58 — SQL JOIN

```python
# day58_sql_joins.py
import sqlite3

conn = sqlite3.connect("app.db")
cur = conn.cursor()

# 建表
cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT
    );
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        amount REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

# 插入数据
cur.execute("INSERT OR IGNORE INTO users VALUES (1, 'Alice', 'a@x.com')")
cur.execute("INSERT OR IGNORE INTO users VALUES (2, 'Bob', 'b@x.com')")
cur.execute("INSERT INTO orders VALUES (1, 1, 99.9, datetime('now'))")
cur.execute("INSERT INTO orders VALUES (2, 1, 199.9, datetime('now'))")
conn.commit()

# JOIN 查询
cur.execute("""
    SELECT u.name, COUNT(o.id) as order_count, SUM(o.amount) as total
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    GROUP BY u.id
    HAVING total > 0
    ORDER BY total DESC
""")
print(cur.fetchall())
```

---

### Day 59 — SQLAlchemy ORM 入门

```python
# day59_sqlalchemy_intro.py
# pip install sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Session
from datetime import datetime, UTC

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

# 创建引擎 + 建表
engine = create_engine("sqlite:///app.db", echo=True)
Base.metadata.create_all(engine)
```

---

### Day 60 — SQLAlchemy CRUD

```python
# day60_sqlalchemy_crud.py
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from day59_sqlalchemy_intro import User, Base, engine

Base.metadata.create_all(engine)

# Create
with Session(engine) as session:
    user = User(name="Alice", email="alice@x.com")
    session.add(user)
    session.commit()
    print(f"创建用户 ID: {user.id}")

# Read
with Session(engine) as session:
    user = session.query(User).filter_by(email="alice@x.com").first()
    print(user.name, user.email)

# Update
with Session(engine) as session:
    user = session.query(User).first()
    user.name = "Alice Updated"
    session.commit()

# Delete
with Session(engine) as session:
    user = session.query(User).first()
    session.delete(user)
    session.commit()
```

---

### Day 61 — 关系

```python
# day61_relationships.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Session, relationship
from datetime import datetime, UTC

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    todos = relationship("Todo", back_populates="user")

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="todos")

# 使用
engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(engine)

with Session(engine) as session:
    user = User(name="Alice")
    session.add(user)
    session.add(Todo(title="学习 SQLAlchemy", user=user))
    session.commit()

    # 通过关系访问
    user = session.query(User).first()
    print(user.todos[0].title)  # 学习 SQLAlchemy
```

---

### Day 62 — Alembic 迁移

```bash
pip install alembic
alembic init alembic
# 编辑 alembic.ini: sqlalchemy.url = sqlite:///app.db
# 编辑 alembic/env.py: 设置 target_metadata
```

```bash
# 自动生成迁移
alembic revision --autogenerate -m "add_deadline_to_todo"
# 应用迁移
alembic upgrade head
```

**alembic/env.py 关键配置**：
```python
from app.models import Base  # 导入你的 Base
target_metadata = Base.metadata
```

---

### Day 63 — SQLite Todo

将 Day 49 的内存 Todo 改成 SQLite 持久化版本。详见 `project-todo-db/`

---

## 第 10 周：FastAPI + 数据库整合

### Day 64 — 整合 FastAPI + SQLAlchemy

```python
# day64_fastapi_db.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Session

# ----- ORM 模型 -----
class Base(DeclarativeBase):
    pass

class TodoModel(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    done = Column(Boolean, default=False)

# ----- 数据库依赖 -----
engine = create_engine("sqlite:///todos.db")
Base.metadata.create_all(engine)

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

# ----- FastAPI -----
from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str

class TodoOut(BaseModel):
    id: int
    title: str
    done: bool
    model_config = {"from_attributes": True}

app = FastAPI()

@app.post("/todos", response_model=TodoOut)
def create(data: TodoCreate, db: Session = Depends(get_db)):
    todo = TodoModel(title=data.title)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@app.get("/todos", response_model=list[TodoOut])
def list_todos(db: Session = Depends(get_db)):
    return db.query(TodoModel).all()
```

### Day 66 — 分页查询

```python
# day66_pagination.py
@app.get("/todos")
def list_todos(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    total = db.query(TodoModel).count()
    items = db.query(TodoModel).offset(skip).limit(limit).all()
    return {"total": total, "items": items, "skip": skip, "limit": limit}
```

### Day 67 — 过滤搜索

```python
# day67_filter.py
from sqlalchemy import or_

@app.get("/todos")
def search_todos(
    q: str = "",
    done: bool | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(TodoModel)
    if q:
        query = query.filter(TodoModel.title.contains(q))
    if done is not None:
        query = query.filter(TodoModel.done == done)
    return query.all()
```

### Day 68 — N+1 问题

```python
# day68_eager_load.py
from sqlalchemy.orm import selectinload

# 错误：N+1 查询
# user = db.query(User).first()
# for t in user.todos:  # 每个 todo 触发一次查询

# 正确：预加载
user = db.query(User).options(selectinload(User.todos)).first()
for t in user.todos:  # 不会触发额外查询
    print(t.title)
```

### Day 69 — Settings 管理

```python
# day69_settings.py
# pip install pydantic-settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///dev.db"
    debug: bool = True
    secret_key: str = "dev-secret"

    class Config:
        env_file = ".env"

settings = Settings()
print(settings.database_url)  # 从 .env 或默认值
```

```
# .env
DATABASE_URL=sqlite:///prod.db
DEBUG=false
```