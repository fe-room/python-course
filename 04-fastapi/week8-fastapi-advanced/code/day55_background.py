"""
后台任务 — BackgroundTasks 示例
注册后异步发送欢迎邮件（模拟）
"""

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import time

app = FastAPI(title="后台任务示例")


# ------------------------------------------------------------------
# 模拟发送邮件（后台执行）
# ------------------------------------------------------------------
def send_welcome_email(email: str, username: str):
    """
    模拟发送欢迎邮件。
    在实际项目中，这里会调用 SMTP / 邮件服务 API。
    """
    time.sleep(2)  # 模拟网络延迟
    print(f"[邮件] 已向 {email} 发送欢迎邮件，欢迎你，{username}！")


# ------------------------------------------------------------------
# 请求模型
# ------------------------------------------------------------------
class RegisterRequest(BaseModel):
    username: str
    email: str


# ------------------------------------------------------------------
# 注册端点
# ------------------------------------------------------------------
@app.post("/register")
def register(user: RegisterRequest, background_tasks: BackgroundTasks):
    """
    用户注册接口：
    1. 立即返回注册成功响应
    2. 后台异步发送欢迎邮件
    """
    # 将耗时任务添加到后台
    background_tasks.add_task(send_welcome_email, user.email, user.username)

    return {
        "msg": "注册成功！欢迎邮件将在后台发送。",
        "username": user.username,
        "email": user.email,
    }


@app.get("/")
def root():
    return {"msg": "请使用 POST /register 注册用户，邮箱会异步发送"}


# 运行入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("day55_background:app", host="127.0.0.1", port=8000, reload=True)
