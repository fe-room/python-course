"""
完整的 Todo CRUD API — 综合实战
====================================
课程: Phase 4, Week 7 — FastAPI 基础
综合实战: 内存版 Todo API (所有知识点整合)

运行方式:
    uvicorn main:app --reload

功能清单:
    - GET    /todos          → 列出所有 Todo (支持分页)
    - GET    /todos/stats    → 统计数据 (总数/已完成/未完成)
    - POST   /todos          → 创建 Todo
    - GET    /todos/{id}     → 获取单个 Todo
    - PUT    /todos/{id}     → 更新 Todo
    - DELETE /todos/{id}     → 删除 Todo

学习要点:
    - Pydantic 模型 + Field 验证
    - 路径参数 + 查询参数
    - HTTPException 异常处理
    - Depends 依赖注入 (分页)
    - CORSMiddleware 跨域配置
"""

from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ======================================================================
# 1. 创建应用 & CORS 配置
# ======================================================================

app = FastAPI(title="Todo API", description="完整的待办事项 CRUD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================================
# 2. Pydantic 模型
# ======================================================================


class TodoCreate(BaseModel):
    """创建 Todo 的请求体。"""

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="待办事项标题",
        examples=["学习 FastAPI"],
    )
    description: str = Field(
        "",
        max_length=500,
        description="详细描述",
    )
    completed: bool = Field(False, description="是否已完成")


class TodoUpdate(BaseModel):
    """更新 Todo 的请求体 — 所有字段可选。"""

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="标题",
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="描述",
    )
    completed: Optional[bool] = Field(
        None,
        description="完成状态",
    )


class TodoResponse(BaseModel):
    """返回给客户端的 Todo 结构。"""

    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    """统计数据响应。"""

    total: int
    completed: int
    pending: int
    completion_rate: float


# ======================================================================
# 3. 内存数据库
# ======================================================================

fake_db: list = []
next_id: int = 1


# ======================================================================
# 4. 依赖注入 — 分页
# ======================================================================

class Pagination:
    """分页依赖。"""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(10, ge=1, le=100, description="每页条数"),
    ):
        self.page = page
        self.size = size
        self.skip = (page - 1) * size


# ======================================================================
# 5. CRUD 接口
# ======================================================================


@app.get("/todos", response_model=List[TodoResponse])
def list_todos(pagination: Pagination = Depends(Pagination())):
    """
    获取 Todo 列表, 支持分页。

    Query:  /todos?page=1&size=10
    """
    items = fake_db[pagination.skip: pagination.skip + pagination.size]
    return [TodoResponse.model_validate(item) for item in items]


@app.get("/todos/stats", response_model=StatsResponse)
def get_stats():
    """
    获取 Todo 统计数据。

    返回总数、已完成数、未完成数、完成率。
    """
    total = len(fake_db)
    completed = sum(1 for t in fake_db if t["completed"])
    pending = total - completed
    completion_rate = round(completed / total, 2) if total > 0 else 0.0

    return StatsResponse(
        total=total,
        completed=completed,
        pending=pending,
        completion_rate=completion_rate,
    )


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    """
    根据 ID 获取单个 Todo。

    如果不存在, 返回 404。
    """
    for item in fake_db:
        if item["id"] == todo_id:
            return TodoResponse.model_validate(item)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Todo {todo_id} 不存在",
    )


@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo_in: TodoCreate):
    """
    创建新的 Todo。

    请求体:
    {
        "title": "学习 FastAPI",
        "description": "完成所有课程练习",
        "completed": false
    }
    """
    global next_id

    new_todo = {
        "id": next_id,
        "title": todo_in.title,
        "description": todo_in.description,
        "completed": todo_in.completed,
        "created_at": datetime.now(),
        "updated_at": None,
    }
    fake_db.append(new_todo)
    next_id += 1

    return TodoResponse.model_validate(new_todo)


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_in: TodoUpdate):
    """
    更新 Todo (部分更新)。

    只更新传入的字段, 未传入的字段保持不变。
    """
    for item in fake_db:
        if item["id"] == todo_id:
            # 更新非 None 的字段
            update_data = todo_in.model_dump(exclude_unset=True)
            item.update(update_data)
            item["updated_at"] = datetime.now()
            return TodoResponse.model_validate(item)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Todo {todo_id} 不存在",
    )


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    """
    删除 Todo。

    成功时返回 204 No Content (无响应体)。
    """
    for i, item in enumerate(fake_db):
        if item["id"] == todo_id:
            fake_db.pop(i)
            return  # 204 无响应体

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Todo {todo_id} 不存在",
    )


# ======================================================================
# 6. 健康检查
# ======================================================================


@app.get("/")
def health_check():
    """API 健康检查。"""
    return {
        "status": "ok",
        "service": "Todo API",
        "version": "1.0.0",
        "total_todos": len(fake_db),
    }


# ======================================================================
# 运行提示:
#   uvicorn main:app --reload
#
# 访问地址:
#   API:       http://127.0.0.1:8000
#   文档:      http://127.0.0.1:8000/docs
#   Redoc:     http://127.0.0.1:8000/redoc
# ======================================================================