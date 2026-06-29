"""
全局异常处理 — Global 404 & 500 异常处理器
统一 JSON 错误响应格式
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="全局异常处理示例")


# ------------------------------------------------------------------
# 统一错误响应结构
# ------------------------------------------------------------------
def error_response(status_code: int, message: str, detail: str = "") -> JSONResponse:
    """返回统一格式的 JSON 错误"""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "status_code": status_code,
                "message": message,
                "detail": detail,
            }
        },
    )


# ------------------------------------------------------------------
# 全局 404 处理器
# ------------------------------------------------------------------
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return error_response(
        status_code=404,
        message="资源未找到",
        detail=f"请求路径 {request.url.path} 不存在",
    )


# ------------------------------------------------------------------
# 全局 500 处理器
# ------------------------------------------------------------------
@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return error_response(
        status_code=500,
        message="服务器内部错误",
        detail=str(exc),
    )


# ------------------------------------------------------------------
# 测试端点
# ------------------------------------------------------------------
@app.get("/")
def root():
    return {"msg": "访问 /hello 或 /cause-error 测试异常处理"}


@app.get("/hello")
def hello():
    return {"msg": "Hello, FastAPI!"}


@app.get("/cause-error")
def cause_error():
    """访问此端点会触发 500 错误"""
    raise ValueError("演示异常：发生了一个意外错误")


# 运行入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("day51_errors:app", host="127.0.0.1", port=8000, reload=True)
