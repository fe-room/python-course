"""
day82_cors_prod.py — 跨域资源共享配置（CORS for Production）
=============================================================
知识点：
  1. 什么是 CORS（Cross-Origin Resource Sharing）
  2. FastAPI 的 CORSMiddleware 使用
  3. 开发环境 vs 生产环境的差异化配置
  4. 安全最佳实践：生产环境只允许特定前端域名

安装依赖：
  pip install fastapi uvicorn python-dotenv

运行方式：
  # 开发环境（允许所有来源）
  ENVIRONMENT=development uvicorn day82_cors_prod:app --reload

  # 生产环境（仅允许指定域名）
  ENVIRONMENT=production FRONTEND_URL=https://myapp.com uvicorn day82_cors_prod:app

什么是 CORS（跨域资源共享）？
  - 浏览器安全策略：默认禁止一个源的网页访问另一个源的资源
  - 例如：前端 http://localhost:3000 请求后端 http://localhost:8000
  - 后端需要在响应头中声明允许的来源（通过 CORS 中间件）
  - 浏览器发送"预检请求"（OPTIONS）来确认服务器是否允许跨域

CORS 配置项详解:
  - allow_origins     : 允许的来源列表（URL）
  - allow_credentials : 是否允许携带 Cookie/Authorization 头
  - allow_methods     : 允许的 HTTP 方法（GET, POST, PUT, DELETE 等）
  - allow_headers     : 允许的请求头
"""

import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ------------------------------------------------------------------
# 环境配置
# ------------------------------------------------------------------
# 通过环境变量区分开发/生产环境
# 开发环境：开发者的本地机器
# 生产环境：线上服务器（Render, AWS, 阿里云等）
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

# 生产环境的前端 URL（从环境变量读取）
PRODUCTION_FRONTEND_URL = os.getenv("FRONTEND_URL", "")

# ------------------------------------------------------------------
# CORS 配置函数
# ------------------------------------------------------------------
def get_cors_origins() -> List[str]:
    """
    根据环境返回允许的来源列表。

    开发环境（development）：
      - 允许所有来源（方便前端调试）
      - 使用 ["*"] 表示允许任意来源

    生产环境（production）：
      - 只允许一个或几个特定的前端域名
      - 从环境变量 FRONTEND_URL 读取
      - 绝对不要使用 ["*"]，否则任何网站都可以调用你的 API
    """
    if ENVIRONMENT == "production":
        # 生产环境：必须配置具体的前端域名
        if not PRODUCTION_FRONTEND_URL:
            raise ValueError(
                "生产环境必须设置 FRONTEND_URL 环境变量！"
                "例如: FRONTEND_URL=https://myapp.onrender.com"
            )
        # 可以支持多个域名（例如：主站 + 备用域名）
        origins = [
            PRODUCTION_FRONTEND_URL,
            # 如果有多个前端域名，可以在此添加
            # "https://myapp.com",
            # "https://admin.myapp.com",
        ]
        print(f"[CORS] 生产环境，允许的来源: {origins}")
        return origins
    else:
        # 开发环境：允许所有来源
        print("[CORS] 开发环境，允许所有来源 (*)")
        return ["*"]


def create_app() -> FastAPI:
    """
    创建 FastAPI 应用并配置 CORS。

    将 CORS 配置封装在函数中，方便测试和复用。
    """
    app = FastAPI(
        title="CORS Demo API",
        version="1.0.0",
        # 生产环境隐藏文档（可选）
        docs_url="/docs" if ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if ENVIRONMENT != "production" else None,
    )

    # 获取 CORS 来源配置
    origins = get_cors_origins()

    # 注册 CORS 中间件
    # 注意：中间件的注册顺序很重要，CORSMiddleware 应尽量靠前
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=["*"] 与 allow_credentials=True 不能同时使用
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],   # 允许所有 HTTP 方法
        allow_headers=["*"],   # 允许所有请求头
    )

    return app


# 创建应用实例
app = create_app()


# ------------------------------------------------------------------
# 路由示例
# ------------------------------------------------------------------
@app.get("/")
def root():
    """根路径，返回 API 信息"""
    return {
        "message": "CORS 已配置 CORS is configured",
        "environment": ENVIRONMENT,
    }


@app.get("/api/data")
def get_data():
    """示例数据接口（前端可能会跨域调用此接口）"""
    return {
        "items": [
            {"id": 1, "name": "项目 A"},
            {"id": 2, "name": "项目 B"},
            {"id": 3, "name": "项目 C"},
        ],
        "total": 3,
    }


@app.post("/api/submit")
def submit_data(data: dict):
    """示例提交接口"""
    return {
        "message": "数据接收成功 Data received",
        "received": data,
    }


# ------------------------------------------------------------------
# 环境配置说明
# ------------------------------------------------------------------
@app.get("/cors-config")
def get_cors_config():
    """返回当前的 CORS 配置信息（用于调试）"""
    # 从 app 的 user_middleware 中提取 CORS 配置
    cors_middleware = None
    for middleware in app.user_middleware:
        if middleware.cls == CORSMiddleware:
            cors_middleware = middleware

    return {
        "environment": ENVIRONMENT,
        "frontend_url": PRODUCTION_FRONTEND_URL if ENVIRONMENT == "production" else None,
        "allow_origins": get_cors_origins(),
    }


# ------------------------------------------------------------------
# 直接运行演示
# ------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("CORS 配置演示")
    print("=" * 60)
    print(f"\n当前环境: {ENVIRONMENT}")
    print(f"允许的来源: {get_cors_origins()}")

    if ENVIRONMENT == "production":
        print("\n[安全提醒]")
        print("  CORS 已限制为指定域名")
        print(f"  前端 URL: {PRODUCTION_FRONTEND_URL}")
    else:
        print("\n[开发模式]")
        print("  允许所有来源，请勿在生产环境使用此配置！")

    print("\n启动服务器:")
    uvicorn.run(app, host="127.0.0.1", port=8000)

# ------------------------------------------------------------------
# 前端测试代码（在浏览器控制台调试用）
# ------------------------------------------------------------------
# 在浏览器控制台运行以下 JavaScript 来测试 CORS：
#
# fetch('http://localhost:8000/api/data')
#   .then(res => res.json())
#   .then(data => console.log('CORS 测试成功:', data))
#   .catch(err => console.error('CORS 错误:', err));