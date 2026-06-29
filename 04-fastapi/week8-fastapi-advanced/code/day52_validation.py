"""
Pydantic 校验 — field_validator 使用
- 邮箱格式校验
- 密码长度校验
"""

from fastapi import FastAPI
from pydantic import BaseModel, field_validator
import re

app = FastAPI(title="Pydantic 校验示例")


# ------------------------------------------------------------------
# 用户注册模型
# ------------------------------------------------------------------
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

    # ---- 邮箱格式校验 ----
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """检查 email 是否符合基本格式"""
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, v):
            raise ValueError(f"邮箱格式无效: {v}")
        return v

    # ---- 密码长度校验 ----
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """密码长度至少 6 位，不超过 20 位"""
        if len(v) < 6:
            raise ValueError("密码长度不能少于 6 位")
        if len(v) > 20:
            raise ValueError("密码长度不能超过 20 位")
        return v


# ------------------------------------------------------------------
# 注册端点
# ------------------------------------------------------------------
@app.post("/register")
def register(user: UserRegister):
    """注册接口，Pydantic 会自动校验请求体"""
    return {
        "msg": "注册成功",
        "username": user.username,
        "email": user.email,
    }


# 运行入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("day52_validation:app", host="127.0.0.1", port=8000, reload=True)
