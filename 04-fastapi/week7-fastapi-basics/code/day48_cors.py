"""
跨域资源共享 (CORS) 配置
============================
课程: Phase 4, Week 7 — FastAPI 基础
Day 48: CORS 与前后端联调

运行方式:
    uvicorn day48_cors:app --reload

什么是 CORS?
    - 浏览器安全策略: 默认禁止不同源 (协议/域名/端口) 的 AJAX 请求
    - 前端在 localhost:3000, 后端在 localhost:8000 → 不同源!
    - 需要后端在响应头中声明允许跨域

测试方法:
    - 在前端项目 (如 React/Vue) 中 fetch("http://127.0.0.1:8000/api/data")
    - 或在浏览器控制台执行 fetch("http://127.0.0.1:8000/api/data")
    - 也可以 curl -v http://127.0.0.1:8000/api/data 查看响应头
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CORS 配置示例")


# ──────────────────────────────────────────────
# CORS 中间件配置
# ──────────────────────────────────────────────

# 定义允许访问后端的来源列表
origins = [
    "http://localhost:3000",      # React 开发服务器默认端口
    "http://127.0.0.1:3000",
    "http://localhost:5173",      # Vite 开发服务器默认端口
    "http://127.0.0.1:5173",
    "http://localhost:8080",      # Vue CLI / Webpack 默认端口
    # 生产环境应替换为实际域名:
    # "https://myapp.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # 允许的来源列表
    allow_credentials=True,       # 是否允许携带 Cookie
    allow_methods=["*"],          # 允许的 HTTP 方法 (GET, POST, PUT, DELETE, ...)
    allow_headers=["*"],          # 允许的自定义请求头
)

# 参数说明:
# - allow_origins=["*"]: 允许所有来源 (仅开发阶段使用!)
# - allow_credentials=True 时, allow_origins 不能为 ["*"], 必须明确指定域名
# - allow_methods=["*"]: 允许所有 HTTP 方法
# - allow_headers=["*"]: 允许所有请求头
# - expose_headers: (可选) 允许前端访问的响应头


# ──────────────────────────────────────────────
# 测试接口
# ──────────────────────────────────────────────

@app.get("/api/data")
def get_data():
    """
    前端跨域请求测试接口。

    配置 CORS 后, 前端可以正常获取到数据。
    如果忘记配 CORS, 浏览器控制台会报错:
        Access to fetch at '...' from origin '...' has been blocked by CORS policy
    """
    return {
        "message": "Hello from FastAPI!",
        "note": "如果能看到这条数据, 说明 CORS 配置成功 🎉",
    }


@app.post("/api/echo")
def echo_data(data: dict):
    """
    前端 POST 请求测试接口。

    注意: 如果 allow_methods 没有包含 "POST",
    浏览器会在正式请求前发送 OPTIONS 预检请求 (Preflight),
    然后被拒绝。
    """
    return {"received": data, "method": "POST"}


@app.get("/api/config")
def get_config():
    """返回当前 CORS 配置信息 (仅用于教学演示)。"""
    cors_config = {
        "description": "CORS 配置信息",
        "note": "生产环境请勿泄露此类信息",
        "allow_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
    }
    return cors_config


# ──────────────────────────────────────────────
# 补充: 什么是 Preflight (预检) 请求?
# ──────────────────────────────────────────────
# 当发送"非简单请求"时 (如 Content-Type: application/json),
# 浏览器会先发送一个 OPTIONS 请求询问服务器是否允许。
# CORSMiddleware 会自动处理 OPTIONS 请求并返回正确的响应头。
# 这就是为什么前端 POST JSON 时需要后端配置 CORS 的原因。
