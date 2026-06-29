"""
HTTP 异常处理与自定义错误格式
=================================
课程: Phase 4, Week 7 — FastAPI 基础
Day 46: 响应处理 & 异常处理

运行方式:
    uvicorn day46_responses:app --reload

测试 URL:
    - GET  /items/1    → 正常返回
    - GET  /items/999  → 返回 404 (HTTPException)
    - GET  /items/abc  → 返回 422 (类型验证错误)
    - GET  /crash      → 返回统一格式的 500 错误
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

app = FastAPI(title="异常处理示例")


# ──────────────────────────────────────────────
# 1. HTTPException — 主动抛出标准 HTTP 错误
# ──────────────────────────────────────────────

# 模拟数据库
fake_items = {1: "苹果", 2: "香蕉", 3: "橘子"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    """
    使用 HTTPException 主动返回 404 错误。

    HTTPException 参数:
    - status_code: HTTP 状态码 (4xx / 5xx)
    - detail: 错误描述信息
    - headers: (可选) 自定义响应头
    """
    if item_id not in fake_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商品 {item_id} 不存在",
            # 可选: 添加自定义响应头
            # headers={"X-Error": "Not Found"},
        )

    return {"item_id": item_id, "name": fake_items[item_id]}


# ──────────────────────────────────────────────
# 2. 自定义异常处理器 — 统一错误返回格式
# ──────────────────────────────────────────────

# 我们定义一个统一的 JSON 错误格式:
# {
#     "success": False,
#     "error": {
#         "code": <HTTP 状态码>,
#         "message": <人类可读的错误信息>
#     }
# }


@app.exception_handler(HTTPException)
async def unified_http_exception_handler(request: Request, exc: HTTPException):
    """
    覆盖 FastAPI 默认的 HTTPException 处理器。

    将所有 HTTPException 统一为:
    {
        "success": false,
        "error": {
            "code": 404,
            "message": "商品 999 不存在"
        }
    }
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
            },
        },
    )


# ──────────────────────────────────────────────
# 3. 通用异常处理器 — 拦截未预料的错误
# ──────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局兜底异常处理器。
    当代码中出现未捕获的异常时, 返回统一的 500 错误。
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "服务器内部错误",
                # 开发阶段可以暴露真实错误信息, 生产环境请关闭!
                "detail": str(exc),
            },
        },
    )


# ──────────────────────────────────────────────
# 4. 故意出错的接口 — 测试全局异常处理器
# ──────────────────────────────────────────────

@app.get("/crash")
def crash():
    """访问此接口会触发 ZeroDivisionError, 测试全局异常处理器。"""
    return 1 / 0  # 故意除零


# ──────────────────────────────────────────────
# 5. 使用 status 模块的常量 (推荐做法)
# ──────────────────────────────────────────────
@app.get("/validate/{value}")
def validate_value(value: int):
    """演示更多 HTTPException 用法。"""
    if value < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="值不能为负数",
        )
    if value > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="值不能超过 100",
        )

    return {"success": True, "value": value}