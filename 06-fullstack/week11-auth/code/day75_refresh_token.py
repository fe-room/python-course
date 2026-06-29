"""
day75_refresh_token.py — 刷新令牌（Token Refresh）
===================================================
知识点：
  1. 访问令牌（access_token）  — 短期有效，用于 API 认证
  2. 刷新令牌（refresh_token） — 长期有效，用于获取新的 access_token
  3. 刷新流程：
     客户端用 refresh_token 请求 /refresh
     服务端验证后返回新的 access_token（和可选的新的 refresh_token）

安全要点：
  - access_token  有效期短（15-30 分钟）
  - refresh_token 有效期长（7-30 天），但必须更加安全保管
  - 如果 refresh_token 泄露，攻击者可以长期获取新的访问令牌
  - 生产环境应将 refresh_token 存储到数据库，支持撤销操作

运行方式：
  uvicorn day75_refresh_token:app --reload

前置知识：
  day71_hashing.py — 密码哈希
  day72_jwt.py    — JWT 创建与解码
  day73_auth_dependency.py — 认证依赖
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel

# ------------------------------------------------------------------
# JWT 相关配置
# 为了演示，刷新令牌也使用 JWT 实现
# 实际项目中可以使用不透明的随机字符串 + 数据库存储
# ------------------------------------------------------------------
from jose import JWTError, jwt

# 访问令牌配置（短期）
ACCESS_SECRET_KEY = "access-secret-change-me"
ACCESS_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 分钟

# 刷新令牌配置（长期）
REFRESH_SECRET_KEY = "refresh-secret-change-me-different-from-access"
REFRESH_ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 天


def create_access_token(user_id: str) -> str:
    """创建短期访问令牌"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "access",  # 标记令牌类型，防止混淆
    }
    return jwt.encode(payload, ACCESS_SECRET_KEY, algorithm=ACCESS_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """创建长期刷新令牌"""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",  # 标记为刷新令牌
        # jti: JWT ID，唯一标识，可用于撤销特定令牌
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=REFRESH_ALGORITHM)


def decode_token(token: str, secret_key: str, expected_type: str) -> dict:
    """
    解码并验证令牌。
    同时检查令牌类型（防止用 refresh_token 当 access_token 使用）。
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        # 验证令牌类型
        if payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌类型错误 Invalid token type",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效或已过期 Invalid or expired token",
        )


# ------------------------------------------------------------------
# FastAPI 应用
# ------------------------------------------------------------------
app = FastAPI(title="Refresh Token Demo", version="1.0.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# 模拟数据库
fake_users_db: dict = {}
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserOut(BaseModel):
    username: str
    email: str


# ------------------------------------------------------------------
# 注册
# ------------------------------------------------------------------
class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    """注册新用户"""
    if payload.username in fake_users_db:
        raise HTTPException(status_code=400, detail="用户名已存在")
    fake_users_db[payload.username] = {
        "username": payload.username,
        "email": payload.email,
        "hashed_password": pwd_context.hash(payload.password),
    }
    return {"message": "注册成功"}


# ------------------------------------------------------------------
# 登录：返回 access_token + refresh_token
# ------------------------------------------------------------------
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录。

    返回两个令牌:
      - access_token  : 短期访问令牌（15 分钟）
      - refresh_token : 长期刷新令牌（7 天）
    """
    user = fake_users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    return {
        "access_token": create_access_token(form_data.username),
        "refresh_token": create_refresh_token(form_data.username),
        "token_type": "bearer",
    }


# ------------------------------------------------------------------
# 令牌刷新端点（核心）
# ------------------------------------------------------------------
class RefreshRequest(BaseModel):
    """刷新请求体"""
    refresh_token: str


@app.post("/refresh")
def refresh_token(payload: RefreshRequest):
    """
    刷新访问令牌。

    流程:
      1. 客户端发送 refresh_token
      2. 服务端验证 refresh_token 的有效性
      3. 验证通过后签发新的 access_token
      4. （可选）同时签发新的 refresh_token（令牌轮换）

    令牌轮换（Token Rotation）:
      — 每次刷新时同时更换 refresh_token
      — 旧的 refresh_token 立即失效
      — 提高安全性：即使 refresh_token 泄露，也只能使用一次
    """
    # 1. 解码并验证 refresh_token
    decoded = decode_token(
        payload.refresh_token,
        REFRESH_SECRET_KEY,
        expected_type="refresh",
    )

    user_id = decoded.get("sub")
    if user_id not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    # 2. 签发新的令牌
    new_access_token = create_access_token(user_id)
    # 令牌轮换：同时返回新的 refresh_token
    new_refresh_token = create_refresh_token(user_id)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


# ------------------------------------------------------------------
# 从 access_token 获取当前用户
# ------------------------------------------------------------------
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """依赖：从 access_token 获取当前用户"""
    decoded = decode_token(token, ACCESS_SECRET_KEY, expected_type="access")
    user = fake_users_db.get(decoded.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


# ------------------------------------------------------------------
# 受保护端点
# ------------------------------------------------------------------
@app.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息（需要有效的 access_token）"""
    return UserOut(**current_user)


# ------------------------------------------------------------------
# 直接运行演示
# ------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("刷新令牌演示服务器")
    print("=" * 60)
    print(f"\n访问令牌有效期   : {ACCESS_TOKEN_EXPIRE_MINUTES} 分钟")
    print(f"刷新令牌有效期   : {REFRESH_TOKEN_EXPIRE_DAYS} 天")
    print("\n交互式 API 文档  : http://127.0.0.1:8000/docs")
    print("\n端点列表:")
    print("  POST /register    — 注册")
    print("  POST /token       — 登录（获取 access + refresh token）")
    print("  POST /refresh     — 刷新 access token")
    print("  GET  /me          — 获取用户信息（用 access token）")
    print("\n测试流程:")
    print("  1. POST /register  注册新用户")
    print("  2. POST /token     登录，保存返回的两个 token")
    print("  3. GET  /me        使用 access_token 访问")
    print("  4. POST /refresh   使用 refresh_token 获取新的 access_token")
    print("  5. 旧的 access_token 失效后，无需重新登录即可获取新令牌")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
