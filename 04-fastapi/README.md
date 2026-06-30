# 第四阶段：FastAPI Web 框架（第 7-8 周）

难度：★★★☆☆ | 前置：第三阶段（异步不是必须）

## 目录

```
04-fastapi/
├── README.md
├── week7-fastapi-basics/
│   └── code/
│       ├── day43_first_api.py
│       ├── day44_params.py
│       ├── day45_models.py
│       ├── day46_responses.py
│       ├── day47_dependencies.py
│       ├── day48_cors.py
│       ├── day49_main.py        # 完整 Todo API（内存版）
│       └── day50_rest_design.md # REST 设计原则
├── week8-fastapi-advanced/
│   └── code/
│       ├── day50_routers/
│       │   ├── __init__.py
│       │   ├── users.py
│       │   └── todos.py
│       ├── day51_errors.py
│       ├── day52_validation.py
│       ├── day53_upload.py
│       ├── day54_middleware.py
│       ├── day55_background.py
│       ├── day56_testing.py        # TestClient 测试
│       └── test_todo_api.py        # 独立测试文件
└── project-todo-api/
    └── app/
        ├── __init__.py
        ├── main.py
        ├── models.py
        ├── routers/
        │   ├── __init__.py
        │   ├── todos.py
        │   └── users.py
        └── requirements.txt
```

## 第 7 周：FastAPI 基础

### Day 43 — 第一个 API

```bash
pip install fastapi uvicorn
```

```python
# day43_first_api.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello, {name}!"}
```

```bash
uvicorn day43_first_api:app --reload
# 访问 http://localhost:8000
# 自动文档 http://localhost:8000/docs
```

---

### Day 44 — 参数

```python
# day44_params.py
from fastapi import FastAPI, Query, Path, Body

app = FastAPI()

@app.get("/items/{item_id}")
def get_item(
    item_id: int = Path(gt=0),                    # 路径参数，大于 0
    q: str | None = None,                         # 可选查询参数
    skip: int = Query(0, ge=0),                   # 查询参数，>= 0
    limit: int = Query(10, ge=1, le=100),          # 1-100
):
    return {"item_id": item_id, "q": q, "skip": skip, "limit": limit}
```

---

### Day 45 — Pydantic 模型

```python
# day45_models.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    category: str = "general"
    tags: list[str] = []

class TodoResponse(BaseModel):
    id: int
    title: str
    done: bool = False
    created_at: datetime
    model_config = {"from_attributes": True}
```

**对比 TS**：Pydantic = TypeScript interface + zod 校验合为一体

---

### Day 46 — 响应状态码

```python
# day46_responses.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ErrorResponse(BaseModel):
    code: int
    message: str

@app.get("/safe_divide/{a}/{b}")
def safe_divide(a: float, b: float):
    if b == 0:
        raise HTTPException(status_code=400, detail="除数不能为 0")
    return {"result": a / b}

# 统一错误格式
@app.exception_handler(HTTPException)
async def custom_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail},
    )
```

---

### Day 47 — 依赖注入

```python
# day47_dependencies.py
from fastapi import FastAPI, Depends

app = FastAPI()

# 函数依赖
def common_params(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

@app.get("/items")
def list_items(params: dict = Depends(common_params)):
    return params

# 类依赖
class Pagination:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit

@app.get("/users")
def list_users(pg: Pagination = Depends()):
    return {"skip": pg.skip, "limit": pg.limit}
```

---

### Day 48 — CORS 中间件

```python
# day48_cors.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 你的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Day 49 — 完整 Todo API（内存版）

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Todo(BaseModel):
    id: int
    title: str
    done: bool = False

class TodoCreate(BaseModel):
    title: str

# 内存存储
todos = []
next_id = 1

@app.get("/todos")
def list_todos(skip: int = 0, limit: int = 10):
    return todos[skip: skip + limit]

@app.post("/todos", status_code=201)
def create_todo(data: TodoCreate):
    global next_id
    todo = Todo(id=next_id, title=data.title)
    todos.append(todo)
    next_id += 1
    return todo

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    for t in todos:
        if t.id == todo_id:
            return t
    raise HTTPException(404, "未找到")

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, data: TodoCreate):
    for t in todos:
        if t.id == todo_id:
            t.title = data.title
            return t
    raise HTTPException(404, "未找到")

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    global todos
    todos = [t for t in todos if t.id != todo_id]
```

---

### Day 50 — REST API 设计原则（理论）

**RESTful 核心原则**：

| 原则 | 说明 |
|------|------|
| 资源路径 | `/todos` 而不是 `/getTodos` |
| HTTP 动词 | GET=查, POST=增, PUT/PATCH=改, DELETE=删 |
| 状态码 | 201=创建成功, 204=删除成功, 400=参数错误 |
| 版本化 | `/v1/todos` 或 Header 版本控制 |

**URL 设计示例**：
```
GET    /todos          # 列表
POST   /todos          # 创建
GET    /todos/{id}     # 详情
PUT    /todos/{id}     # 全量更新
PATCH  /todos/{id}    # 局部更新
DELETE /todos/{id}    # 删除
```

**对比前端**：REST = 前后端约定的接口规范，类似 GraphQL 但更简单

---

## 第 8 周：FastAPI 进阶

### Day 50 — APIRouter

```python
# routers/todos.py
from fastapi import APIRouter

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("/")
def list_todos():
    return []

@router.post("/")
def create_todo():
    return {}
```

```python
# main.py
from fastapi import FastAPI
from routers import todos, users

app = FastAPI()
app.include_router(todos.router)
app.include_router(users.router)
```

### Day 51 — 全局错误处理

```python
# day51_errors.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"code": 404, "message": "资源不存在"}
    )

@app.exception_handler(500)
async def server_error(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误"}
    )
```

### Day 52 — 字段校验

```python
# day52_validation.py
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    email: str = Field(pattern=r"^\S+@\S+\.\S+$")
    password: str = Field(min_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if not v.endswith(".com"):
            raise ValueError("仅支持 .com 邮箱")
        return v
```

### Day 53 — 文件上传

```python
# day53_upload.py
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    return {
        "filename": file.filename,
        "size": len(content),
        "content_type": file.content_type,
    }
```

### Day 54 — 中间件

```python
# day54_middleware.py
import time
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    print(f"{request.method} {request.url.path} - {elapsed*1000:.0f}ms")
    return response
```

### Day 55 — BackgroundTasks

```python
# day55_background.py
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def send_welcome_email(email: str):
    print(f"发送欢迎邮件到 {email}")  # 实际用邮件服务

@app.post("/register")
def register(name: str, email: str, bg: BackgroundTasks):
    bg.add_task(send_welcome_email, email)
    return {"message": "注册成功"}

---

### Day 56 — API 测试（TestClient）

```python
# day56_testing.py
from fastapi.testclient import TestClient
from day56_testing import app

client = TestClient(app)

def test_list_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

def test_create_todo():
    response = client.post("/todos", json={"title": "Buy milk"})
    assert response.status_code == 201
    assert response.json()["title"] == "Buy milk"

# 运行：pytest day56_testing.py -v
```

**对比 Jest**：TestClient = 前端的 supertest，无需启动服务器即可测试 API。

详见 `code/day56_testing.py`（完整 CRUD 测试）和 `code/test_todo_api.py`（测试文件分离实践）
```