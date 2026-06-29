"""
中间件 — @app.middleware("http") 请求日志
记录请求方法、路径、耗时
"""

import time
from fastapi import FastAPI, Request

app = FastAPI(title="中间件 — 请求日志示例")


# ------------------------------------------------------------------
# 请求日志中间件
# ------------------------------------------------------------------
@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    """
    记录每个 HTTP 请求的方法、路径和处理耗时
    """
    start_time = time.perf_counter()  # 高精度计时起点

    # 继续执行请求（进入路由处理函数）
    response = await call_next(request)

    # 计算耗时
    elapsed = time.perf_counter() - start_time

    # 打印日志
    print(f"[{request.method}] {request.url.path} — 耗时: {elapsed:.4f}s")

    return response


# ------------------------------------------------------------------
# 测试端点
# ------------------------------------------------------------------
@app.get("/")
def root():
    return {"msg": "访问任意路径，观察控制台日志"}


@app.get("/hello")
def hello():
    return {"msg": "Hello, FastAPI!"}


@app.get("/slow")
async def slow():
    """模拟慢请求"""
    import asyncio
    await asyncio.sleep(2)
    return {"msg": "这是一个慢请求"}


# 运行入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("day54_middleware:app", host="127.0.0.1", port=8000, reload=True)
