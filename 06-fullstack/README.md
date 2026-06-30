# 第六阶段：完整全栈项目（第 11-12 周）

难度：★★★★☆ | 前置：前五阶段

## 目录

```
06-fullstack/
├── README.md
├── week11-auth/code/
│   ├── day71_hashing.py
│   ├── day72_jwt.py
│   ├── day73_auth_dependency.py
│   ├── day74_permissions.py
│   ├── day75_refresh_token.py
│   ├── day76_logging.py
│   └── day77_cicd.md
├── week12-deploy/code/
│   ├── day78_frontend_integration.md
│   ├── day79_graduation_project.md
│   ├── day80_dockerfile
│   ├── day81_render_deploy.md
│   └── day82_cors_prod.py
├── project-graduation/
│   └── README.md
```

## 第 11 周：用户认证

### Day 71 — 密码哈希

```python
# day71_hashing.py
# pip install passlib[bcrypt]
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

hashed = hash_password("mypassword123")
print(hashed)  # $2b$12$...
print(verify_password("mypassword123", hashed))  # True
print(verify_password("wrong", hashed))          # False
```

---

### Day 72 — JWT

```python
# day72_jwt.py
# pip install python-jose[cryptography]
from jose import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

token = create_access_token(1)
print(token)  # eyJhbGciOiJIUzI1NiIs...
print(decode_token(token))  # {'sub': '1', 'exp': ..., ...}
```

---

### Day 73 — 认证依赖

```python
# day73_auth_dependency.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from day72_jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
app = FastAPI()

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "无效 token")
        return int(user_id)
    except JWTError:
        raise HTTPException(401, "无效 token")

@app.get("/me")
def get_me(user_id: int = Depends(get_current_user)):
    return {"user_id": user_id}

# 测试：先获取 token，再用 Bearer token 访问 /me
```

---

### Day 74 — 权限控制

```python
# day74_permissions.py
from fastapi import Depends, HTTPException

def require_admin(user_id: int = Depends(get_current_user)):
    # 从数据库查用户角色
    # if not is_admin(user_id):
    #     raise HTTPException(403, "需要管理员权限")
    return user_id

@app.delete("/users/{target_id}")
def delete_user(
    target_id: int,
    admin_id: int = Depends(require_admin),
):
    return {"message": f"已删除用户 {target_id}"}
```

---

### Day 75 — Token 刷新

```python
# day75_refresh_token.py
from pydantic import BaseModel

class TokenRefresh(BaseModel):
    refresh_token: str

@app.post("/refresh")
def refresh_token(data: TokenRefresh):
    try:
        payload = decode_token(data.refresh_token)
        user_id = int(payload["sub"])
        new_token = create_access_token(user_id)
        return {"access_token": new_token}
    except JWTError:
        raise HTTPException(401, "refresh_token 无效")
```

---

### Day 76 — 日志配置

```python
# day76_logging.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger("myapp")
logger.info("应用启动")
logger.error("数据库连接失败")
```

---

### Day 77 — CI/CD（GitHub Actions）

**目标**：自动化测试 + 自动化部署

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pip install pytest
      - run: pytest
```

**关键概念**：
- GitHub Actions = 前端的 GitHub Actions 一样，YAML 配置
- `on: [push, pull_request]` — 触发条件
- `matrix` — 多 Python 版本并行测试

详见 `code/day77_cicd.md`

---

## 第 12 周：部署

### Day 80 — Docker

```dockerfile
# day80_dockerfile
FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t myapi .
docker run -p 8000:8000 myapi
```

### Day 81 — 部署到 Render

1. 注册 Render 账号
2. 连接 GitHub 仓库
3. 创建 Web Service
4. 设置环境变量（`DATABASE_URL`、`SECRET_KEY`）
5. 部署

### Day 82 — 生产 CORS

```python
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    frontend_url: str = "http://localhost:3000"

settings = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],  # 仅允许前端域名
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

### Day 83 — 项目综合回顾

回顾整个课程的知识体系：

| 阶段 | 核心技能 | 产出 |
|------|---------|------|
| 1-2 | Python 语法、脚本、CLI | CLI Todo |
| 3-4 | OOP、Pythonic、装饰器 | Todo Class |
| 5-6 | 生成器、异步 | 异步下载器 |
| 7-8 | FastAPI、REST | Todo API |
| 9-10 | SQLAlchemy、数据库 | Todo DB |
| 11-12 | 认证、部署、CI/CD | 毕业项目 |

**能力自检清单**：
- [ ] 能独立用 Python 写脚本
- [ ] 能设计 class 并使用 dataclass/enum
- [ ] 能写装饰器和上下文管理器
- [ ] 能编写异步代码
- [ ] 能搭建 FastAPI 应用
- [ ] 能用 SQLAlchemy 操作数据库
- [ ] 能实现 JWT 认证
- [ ] 能配置 CI/CD
- [ ] 能 Docker 部署

---

## 毕业项目

在第 12 周末，你将完成一个完整的前后端分离项目：

**可选方向**：
1. 博客系统（文章 CRUD + 用户系统 + Markdown 编辑）
2. 简易电商（商品浏览 + 购物车 + 下单）
3. 你已有前端项目的后端实现

**技术要求**：
- FastAPI 后端
- SQLite/PostgreSQL 数据库
- JWT 用户认证
- 前端（你的现有技术栈）调用后端 API
- Docker 容器化
- 部署上线

**项目结构建议**（前后端分离）：
```
project/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   ├── auth.py
│   │   └── dependencies.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
└── frontend/
    └── (你的前端项目)
```