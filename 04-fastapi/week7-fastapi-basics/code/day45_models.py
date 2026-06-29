"""
Pydantic 模型与请求体验证
============================
课程: Phase 4, Week 7 — FastAPI 基础
Day 45: Pydantic Models & Field 验证

运行方式:
    uvicorn day45_models:app --reload

重点:
    - Pydantic BaseModel 用于定义请求/响应结构
    - Field() 提供字段级别的验证
    - from_attributes=True 允许从 ORM / 普通对象创建模型
    - 访问 http://127.0.0.1:8000/docs 查看自动生成的文档
"""

from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, status
from pydantic import BaseModel, Field

app = FastAPI(title="Pydantic 模型示例")


# ──────────────────────────────────────────────
# TodoCreate — 创建待办事项时的请求体
# ──────────────────────────────────────────────
class TodoCreate(BaseModel):
    """
    创建 Todo 时的请求体结构。

    Field 说明:
    - title: 必填, 最长 100 字符
    - description: 可选, 默认空字符串
    - completed: 可选, 默认 False
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="待办事项标题",
        examples=["买 groceries"],
    )
    description: str = Field(
        "",
        max_length=500,
        description="详细描述（可选）",
    )
    completed: bool = Field(
        False,
        description="是否已完成",
    )


# ──────────────────────────────────────────────
# TodoResponse — 返回给客户端的完整 Todo
# ──────────────────────────────────────────────
class TodoResponse(BaseModel):
    """
    返回给客户端的 Todo 结构。

    from_attributes=True 表示可以从任意对象创建实例:
        TodoResponse.model_validate(todo_obj)

    这是 Pydantic v2 的写法, v1 中对应 class Config: orm_mode = True
    """

    id: int = Field(..., description="唯一标识")
    title: str = Field(..., description="标题")
    description: str = Field("", description="描述")
    completed: bool = Field(False, description="完成状态")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# 模拟存储 (仅用于演示)
# ──────────────────────────────────────────────
fake_db: list = []


@app.post("/todos", status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
def create_todo(todo_in: TodoCreate):
    """
    创建一条新的 Todo。

    请求体会自动验证并转换成 TodoCreate 对象。
    """
    # 模拟创建
    new_todo = {
        "id": len(fake_db) + 1,
        "title": todo_in.title,
        "description": todo_in.description,
        "completed": todo_in.completed,
        "created_at": datetime.now(),
    }
    fake_db.append(new_todo)

    # 使用 model_validate 将字典转换成 TodoResponse
    return TodoResponse.model_validate(new_todo)


@app.get("/todos", response_model=List[TodoResponse])
def list_todos():
    """获取所有 Todo 列表。"""
    return [TodoResponse.model_validate(t) for t in fake_db]


# ──────────────────────────────────────────────
# 附加示例: 更丰富的 Field 用法
# ──────────────────────────────────────────────

class ProductCreate(BaseModel):
    """商品创建模型 — 展示更多 Field 选项。"""

    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[a-zA-Z0-9\u4e00-\u9fa5\s]+$",  # 正则: 字母、数字、中文、空格
        description="商品名称",
    )
    price: float = Field(
        ...,
        gt=0,
        le=99999.99,
        description="价格, 必须大于 0",
        examples=[19.99],
    )
    stock: int = Field(
        0,
        ge=0,
        description="库存数量, 不能为负",
    )
    tags: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="标签, 最多 5 个",
    )


@app.post("/products", response_model=ProductCreate)
def create_product(product: ProductCreate):
    """创建商品 (直接返回输入以演示验证)。"""
    return product