"""
day73_auth_dependency.py — FastAPI 认证依赖（Authentication Dependency）
=====================================================================
知识点：
  1. OAuth2PasswordBearer — FastAPI 内置的 Bearer Token 提取器
  2. get_current_user     — 依赖函数，解码 JWT 并返回当前用户
  3. Protected /me 端点   — 需要认证才能访问的用户信息接口
  4. 综合使用 day71 的密码哈希和 day72 的 JWT 功能

安装依赖：
  pip install fastapi uvicorn "passlib[bcrypt]" "python-jose[cryptography]"

运行方式：
  uvicorn day73_auth_dependency:app --reload
"""

import os
from datetime import timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

# ------------------------------------------------------------------
# 引入 day71 和 day72 的核心逻辑（为演示直接在此实现）
# 实际项目中可将 day71_hashing.py 和 day72_jwt.py 作为模块 import
# ------------------------------------------------------------------
from day71_hashing import hash_password, verify_password
from day72_jwt import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decode_token,
)

# ------------------------------------------------------------------
# FastAPI 应用初始化
# ------------------------------------------------------------------
app = FastAPI(title="Auth Demo API", version="1.0.0")

# OAuth2PasswordBearer:
#   - 从请求头 Authorization: Bearer <token> 中提取 token
#   - tokenUrl="/token" 告诉客户端登录接口的路径
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# ------------------------------------------------------------------
# 模拟数据库 — 生产环境请用真实数据库
# ------------------------------------------------------------------
# 键: 用户名
# 值: {"hashed_password": ..., "email": ...}
fake_users_db: dict = {}


class UserOut(BaseModel):
    """返回给客户端的用户信息（不包含密码）"""
    username: str
    email: str
    disabled: bool = False


class UserInDB(UserOut):
    """内部使用的用户模型（包含哈希密码）"""
    hashed_password: str


def get_user(db: dict, username: str) -> Optional[UserInDB]:
    """从模拟数据库中查找用户"""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


# ------------------------------------------------------------------
# 注册接口（Register）
# ------------------------------------------------------------------
class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    """
    用户注册：对密码进行哈希后存入模拟数据库。
    """
    if payload.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在 Username already exists",
        )
    hashed_pw = hash_password(payload.password)
    fake_users_db[payload.username] = {
        "username": payload.username,
        "email": payload.email,
        "hashed_password": hashed_pw,
        "disabled": False,
    }
    return {"message": f"用户 {payload.username} 注册成功"}


# ------------------------------------------------------------------
# 登录接口（获取 Token）
# ------------------------------------------------------------------
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录：验证用户名和密码，返回 JWT 访问令牌。
    OAuth2PasswordRequestForm 自动解析 form-data 中的
    username 和 password 字段。
    """
    # 1. 查找用户
    user = get_user(fake_users_db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误 Incorrect username or password",
            # WWW-Authenticate 告诉客户端使用 Bearer 认证方式
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 验证密码
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误 Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 生成 JWT
    access_token = create_access_token(user_id=user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ------------------------------------------------------------------
# 获取当前用户的依赖函数（核心）
# ------------------------------------------------------------------
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    依赖函数：从请求中提取 Bearer Token，解码 JWT，返回当前用户。

    在 FastAPI 中，Depends() 可以嵌套使用。
    每个需要认证的路由都可以使用 Depends(get_current_user)。

    Raises
    ------
    HTTPException 401
        令牌无效、过期或用户不存在时抛出。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据 Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. 解码 JWT，获取 payload
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2. 从数据库查找用户
    user = get_user(fake_users_db, username)
    if user is None:
        raise credentials_exception

    return user


# ------------------------------------------------------------------
# 获取当前激活用户（检查 disabled 状态）
# ------------------------------------------------------------------
async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    """在 get_current_user 基础上，额外检查用户是否被禁用"""
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用 Inactive user",
        )
    return current_user


# ------------------------------------------------------------------
# 受保护的 /me 端点
# ------------------------------------------------------------------
@app.get("/me", response_model=UserOut)
async def read_users_me(
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    获取当前登录用户的信息。

    此接口需要通过 Bearer Token 认证。
    Depends(get_current_active_user) 会自动执行：
      1. 提取 Token
      2. 解码 JWT
      3. 查找用户
      4. 检查用户状态
    """
    return current_user


# ------------------------------------------------------------------
# 公开的健康检查端点（无需认证）
# ------------------------------------------------------------------
@app.get("/health")
def health_check():
    """公开端点，用于监控服务是否正常"""
    return {"status": "ok", "message": "服务运行正常 Service is running"}


# ------------------------------------------------------------------
# 直接运行演示
# ------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("启动 FastAPI 认证演示服务器")
    print("=" * 60)
    print("\n交互式 API 文档: http://127.0.0.1:8000/docs")
    print("\n可用端点:")
    print("  POST /register  — 注册新用户")
    print("  POST /token     — 登录获取 JWT")
    print("  GET  /me        — 获取当前用户信息（需要 Bearer Token）")
    print("  GET  /health    — 健康检查（公开）")
    uvicorn.run(app, host="127.0.0.1", port=8000)