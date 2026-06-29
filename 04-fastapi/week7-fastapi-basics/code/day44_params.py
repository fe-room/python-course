"""
路径参数与查询参数 — 参数验证与默认值
======================================
课程: Phase 4, Week 7 — FastAPI 基础
Day 44: 路径参数 & 查询参数

运行方式:
    uvicorn day44_params:app --reload

测试 URL:
    - http://127.0.0.1:8000/items/5          → 正常
    - http://127.0.0.1:8000/items/0          → 验证错误（gt=0）
    - http://127.0.0.1:8000/search?q=python&page=2&size=20  → 完整参数
    - http://127.0.0.1:8000/search           → 仅使用默认值
    - http://127.0.0.1:8000/users/101        → 可选参数示例
"""

from fastapi import FastAPI, Query, Path

app = FastAPI(title="参数验证示例")


# ──────────────────────────────────────────────
# 1. 路径参数 + 验证 (Path)
# ──────────────────────────────────────────────
@app.get("/items/{item_id}")
def read_item(
    item_id: int = Path(
        ...,
        title="商品 ID",
        description="请输入大于 0 的整数",
        gt=0,  # 约束: 必须大于 0
    ),
):
    """
    路径参数 item_id 使用了 Path 验证:
    - gt=0 表示值必须大于 0
    - 如果传入 0 或负数, FastAPI 会自动返回 422 验证错误
    """
    return {"item_id": item_id}


# ──────────────────────────────────────────────
# 2. 查询参数 + 默认值 (Query)
# ──────────────────────────────────────────────
@app.get("/search")
def search_items(
    q: str = Query(..., title="搜索关键词", min_length=1),
    page: int = Query(1, title="页码", ge=1),
    size: int = Query(10, title="每页数量", ge=1, le=100),
):
    """
    查询参数说明:
    - q: 必填, 最小长度 1
    - page: 可选, 默认 1, 必须 ≥ 1
    - size: 可选, 默认 10, 范围 1~100
    """
    return {
        "query": q,
        "page": page,
        "size": size,
        "start": (page - 1) * size,
        "end": page * size,
    }


# ──────────────────────────────────────────────
# 3. 可选查询参数 (使用 Optional)
# ──────────────────────────────────────────────
from typing import Optional


@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    # 可选参数: 不传时默认为 None
    detail: Optional[bool] = None,
):
    """
    演示可选查询参数:
    - /users/101         → detail 为 None
    - /users/101?detail=true → detail 为 True

    Optional[bool] 表示该参数可以省略, 省略时为 None。
    """
    result = {"user_id": user_id}

    if detail:
        result["detail"] = "这是用户的详细信息（仅作演示）"

    return result