"""
day74_permissions.py — 基于角色的权限控制（Role-Based Access Control）
====================================================================
知识点：
  1. 用户角色模型（admin / user / viewer）
  2. require_admin 依赖函数 — 只有 admin 角色才能访问
  3. require_role() 工厂函数 — 可复用的角色检查依赖
  4. 403 Forbidden — 权限不足时返回的 HTTP 状态码

运行方式：
  uvicorn day74_permissions:app --reload

前置知识：
  请先理解 day73_auth_dependency.py 中的 get_current_user 依赖。
"""

import os
from enum import Enum
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

# ------------------------------------------------------------------
# 复用 day71 / day72 的代码
# ------------------------------------------------------------------
from day71_hashing import hash_password, verify_password
from day72_jwt import create_access_token, decode_token

# ------------------------------------------------------------------
# 角色枚举
# ------------------------------------------------------------------
class Role(str, Enum):
    """
    用户角色枚举。

    角色层级（从高到低）:
      admin  — 管理员：拥有所有权限
      user   — 普通用户：可以访问一般资源
      viewer — 观察者：只读权限
    """
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


# ------------------------------------------------------------------
# FastAPI 应用初始化
# ------------------------------------------------------------------
app = FastAPI(title="Permissions Demo API", version="1.0.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# ------------------------------------------------------------------
# 模拟数据库（扩展了角色字段）
# ------------------------------------------------------------------
fake_users_db: dict = {}


class UserOut(BaseModel):
    """对外展示的用户信息"""
    username: str
    email: str
    role: Role
    disabled: bool = False


class UserInDB(UserOut):
    """内部用户模型（含哈希密码）"""
    hashed_password: str


# ------------------------------------------------------------------
# 注册与登录
# ------------------------------------------------------------------
class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    role: Role = Role.USER  # 默认角色为普通用户


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    """注册新用户（可指定角色，生产环境中注册接口不应允许自选角色）"""
    if payload.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    hashed_pw = hash_password(payload.password)
    fake_users_db[payload.username] = {
        "username": payload.username,
        "email": payload.email,
        "role": payload.role,
        "hashed_password": hashed_pw,
        "disabled": False,
    }
    return {"message": f"用户 {payload.username} 注册成功，角色: {payload.role.value}"}


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """登录并返回 JWT（令牌中包含角色信息）"""
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict or not verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 注意：将 role 也放入 JWT payload，方便后续权限判断
    access_token = create_access_token(
        user_id=user_dict["username"],
        # 可以通过扩展 create_access_token 传入额外数据，
        # 这里为简化，直接使用 sub 字段，
        # 实际项目中可将角色信息放在自定义字段中
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------------------------------------------------------
# 通用的 get_current_user 依赖
# ------------------------------------------------------------------
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """从 JWT 中提取并验证当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_dict = fake_users_db.get(username)
    if user_dict is None:
        raise credentials_exception

    return UserInDB(**user_dict)


# ------------------------------------------------------------------
# 方式一：专门的 require_admin 依赖
# ------------------------------------------------------------------
async def require_admin(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    仅允许 admin 角色访问。

    如果当前用户不是 admin，返回 HTTP 403 Forbidden。
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：需要管理员角色 Insufficient permissions: admin role required",
        )
    return current_user


# ------------------------------------------------------------------
# 方式二：通用的 require_role 工厂函数（更灵活）
# ------------------------------------------------------------------
def require_role(allowed_roles: List[Role]):
    """
    创建一个依赖函数，仅允许指定角色的用户访问。

    Parameters
    ----------
    allowed_roles : List[Role]
        允许访问的角色列表。

    Returns
    -------
    callable
        一个 FastAPI 依赖函数。

    Usage
    -----
    @app.get("/admin-only")
    def admin_endpoint(user: UserInDB = Depends(require_role([Role.ADMIN]))):
        ...

    @app.get("/staff")
    def staff_endpoint(user: UserInDB = Depends(require_role([Role.ADMIN, Role.USER]))):
        ...
    """
    async def role_checker(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"权限不足：需要 {[r.value for r in allowed_roles]} 角色，"
                    f"当前角色为 {current_user.role.value}"
                ),
            )
        return current_user

    return role_checker


# ------------------------------------------------------------------
# 路由示例：不同角色访问不同资源
# ------------------------------------------------------------------

# 1. 任何人都可以访问的公开端点
@app.get("/public")
def public_endpoint():
    """公开资源：无需认证"""
    return {"message": "这是公开信息，所有人可见"}


# 2. 需要登录（任何角色）即可访问
@app.get("/profile")
async def profile(current_user: UserInDB = Depends(get_current_user)):
    """个人资料：任何已登录用户都可以访问"""
    return {
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
    }


# 3. 仅 admin 可以访问（使用 require_admin）
@app.get("/admin/dashboard")
async def admin_dashboard(admin: UserInDB = Depends(require_admin)):
    """管理后台：仅 admin 角色可访问"""
    return {
        "message": f"欢迎管理员 {admin.username}",
        "dashboard_data": {
            "total_users": len(fake_users_db),
            "server_status": "healthy",
        },
    }


# 4. 使用 require_role 工厂函数
@app.get("/moderate")
async def moderate_content(
    current_user: UserInDB = Depends(require_role([Role.ADMIN, Role.USER])),
):
    """内容审核：admin 和 user 角色可访问，viewer 不可访问"""
    return {
        "message": f"用户 {current_user.username}（{current_user.role.value}）有权限审核内容",
    }


# 5. viewer 专属端点
@app.get("/reports")
async def view_reports(
    current_user: UserInDB = Depends(require_role([Role.ADMIN, Role.USER, Role.VIEWER])),
):
    """查看报告：所有角色都可以查看（只读操作）"""
    return {
        "message": f"用户 {current_user.username} 正在查看报告（只读）",
        "reports": ["report_1.pdf", "report_2.pdf"],
    }


# ------------------------------------------------------------------
# 直接运行时的演示
# ------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("权限控制演示服务器")
    print("=" * 60)
    print("\n交互式 API 文档: http://127.0.0.1:8000/docs")
    print("\n可用端点与权限要求:")
    print("  POST /register           — 注册（可选角色）")
    print("  POST /token              — 登录")
    print("  GET  /public             — 公开，无需认证")
    print("  GET  /profile            — 任何已登录用户")
    print("  GET  /admin/dashboard    — 仅 admin")
    print("  GET  /moderate           — admin + user")
    print("  GET  /reports            — admin + user + viewer")
    print("\n测试建议:")
    print("  1. 分别注册 admin/user/viewer 三个用户")
    print("  2. 用不同用户的 Token 访问 /admin/dashboard 观察结果")
    uvicorn.run(app, host="127.0.0.1", port=8000)