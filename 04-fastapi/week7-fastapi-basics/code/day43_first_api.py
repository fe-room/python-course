"""
第一个 FastAPI 应用 — 最简单的入门示例
===================================
课程: Phase 4, Week 7 — FastAPI 基础
Day 43: 初识 FastAPI

运行方式:
    uvicorn day43_first_api:app --reload

启动后访问:
    - http://127.0.0.1:8000          → {"message": "Hello World"}
    - http://127.0.0.1:8000/hello/小明  → {"message": "Hello 小明"}
    - http://127.0.0.1:8000/docs      → 自动生成的 Swagger 文档
"""

from fastapi import FastAPI

# 创建 FastAPI 实例
# 标题会显示在 /docs 页面中
app = FastAPI(title="我的第一个 FastAPI")


@app.get("/")
def read_root():
    """根路由 — GET 请求入口"""
    return {"message": "Hello World"}


@app.get("/hello/{name}")
def say_hello(name: str):
    """路径参数示例 — {name} 会被 URL 中的实际值替换"""
    return {"message": f"Hello {name}"}