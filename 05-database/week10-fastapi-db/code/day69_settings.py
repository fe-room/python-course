"""
Day 69 — pydantic-settings 配置管理
====================================
演示如何使用 pydantic-settings 管理应用配置：
  - 从 .env 文件加载配置
  - 支持环境变量覆盖
  - 类型校验 + 默认值
  - 数据库 URL、调试模式等常见配置项

为什么用 pydantic-settings 而不是 os.environ？
  1. 类型自动转换（字符串 -> int / bool）
  2. 嵌套校验
  3. IDE 自动补全
  4. 支持 .env 文件

运行方式:
    uvicorn day69_settings:app --reload

注意：请在同目录下创建 .env 文件（参考 .env.example 注释内容）
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

import uvicorn
from fastapi import FastAPI
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import (
    Session,
    declarative_base,
    sessionmaker,
)

# ===================================================================
# 1. 配置类 —— 集中管理所有环境变量
# ===================================================================


class Settings(BaseSettings):
    """
    应用配置，继承自 pydantic-settings 的 BaseSettings。

    配置加载优先级（覆盖顺序，从高到低）：
      1. 环境变量（最高）
      2. .env 文件
      3. 代码中的默认值（最低）

    命名约定：小写 + 下划线，环境变量会自动映射
      例如：database_url -> DATABASE_URL（环境变量）
    """

    # ── 数据库配置 ────────────────────────────────────────────────
    # 默认使用 SQLite 本地文件
    database_url: str = Field(
        default="sqlite:///./settings_todos.db",
        description="数据库连接 URL。生产环境使用 PostgreSQL: postgresql://user:pass@host/db",
    )

    # 数据库连接池大小（仅 PostgreSQL/MySQL 有效）
    db_pool_size: int = Field(default=5, ge=1, le=100, description="数据库连接池大小")

    # ── 应用配置 ──────────────────────────────────────────────────
    # 调试模式：开启后打印 SQL 日志、显示详细错误
    debug: bool = Field(default=False, description="调试模式开关")

    # 应用名称
    app_name: str = Field(default="Todo App", description="应用名称")

    # 监听主机和端口
    host: str = Field(default="127.0.0.1", description="监听地址")
    port: int = Field(default=8000, ge=1024, le=65535, description="监听端口")

    # ── 可选：第三方服务配置 ──────────────────────────────────────
    # 这些只是示例，实际项目可以在这里加 Redis、Sentry 等配置
    redis_url: Optional[str] = Field(default=None, description="Redis 连接 URL")
    sentry_dsn: Optional[str] = Field(
        default=None, description="Sentry 错误追踪 DSN"
    )

    # ── .env 文件加载配置 ─────────────────────────────────────────
    # 指定 .env 文件路径（默认在当前目录找 .env）
    # env_file 编码、是否强制要求等
    model_config = SettingsConfigDict(
        env_file=".env",          # 加载 .env 文件
        env_file_encoding="utf-8",  # 文件编码
        extra="ignore",           # 忽略 .env 中多余的变量
        case_sensitive=False,     # 环境变量大小写不敏感
    )


# .env.example 参考内容（在项目中创建一个 .env 文件）：
#
#   # 数据库
#   DATABASE_URL=sqlite:///./todos.db
#   DB_POOL_SIZE=10
#
#   # 应用
#   DEBUG=true
#   APP_NAME=我的 Todo 应用
#   HOST=0.0.0.0
#   PORT=8000
#
#   # 第三方服务（可选）
#   REDIS_URL=redis://localhost:6379/0


# ===================================================================
# 2. 全局配置实例
# ===================================================================


@lru_cache()
def get_settings() -> Settings:
    """
    获取全局唯一的 Settings 实例。

    使用 lru_cache 确保配置只加载一次（单例模式）。
    调用 get_settings() 时才会真正读取 .env 和环境变量。
    """
    return Settings()  # 自动读取 .env 和环境变量


# 直接获取配置（后续代码直接使用）
settings = get_settings()


# ===================================================================
# 3. 根据配置初始化数据库
# ===================================================================

# 根据 debug 模式决定是否打印 SQL 日志
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=settings.debug,  # debug=True 时打印所有 SQL
    pool_size=settings.db_pool_size,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    done = Column(Boolean, default=False)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===================================================================
# 4. FastAPI 应用
# ===================================================================

from fastapi import Depends
from pydantic import BaseModel, ConfigDict
from typing import List


class TodoOut(BaseModel):
    id: int
    title: str
    done: bool

    model_config = ConfigDict(from_attributes=True)


class TodoCreate(BaseModel):
    title: str
    done: bool = False


app = FastAPI(
    title=settings.app_name,  # 从配置读取应用名
    version="0.1.0",
    debug=settings.debug,     # 从配置读取调试模式
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logging.info(
        f"应用启动 | 名称: {settings.app_name} | "
        f"数据库: {settings.database_url} | "
        f"调试模式: {settings.debug}"
    )


@app.get("/")
def root():
    """返回当前配置信息（仅用于演示，生产环境不要暴露敏感配置）"""
    return {
        "message": f"Day 69 — 配置管理 ({settings.app_name})",
        "app_name": settings.app_name,
        "debug": settings.debug,
        "database_url": settings.database_url,
        "db_pool_size": settings.db_pool_size,
        "host": settings.host,
        "port": settings.port,
        "redis_configured": settings.redis_url is not None,
    }


@app.get("/settings")
def show_settings():
    """专用于演示的端点：展示所有配置项"""
    s = get_settings()
    return {
        "database_url": s.database_url,
        "db_pool_size": s.db_pool_size,
        "debug": s.debug,
        "app_name": s.app_name,
        "host": s.host,
        "port": s.port,
        "redis_url": s.redis_url,
        "sentry_dsn": s.sentry_dsn,
    }


@app.get("/todos", response_model=List[TodoOut])
def list_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()


@app.post("/todos", response_model=TodoOut)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    todo = Todo(**payload.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


# ===================================================================
# 5. 配置变更自省 —— <extra> 机制
# ===================================================================
# pydantic-settings 的 extra="ignore" 意味着 .env 中多余的值
# 会被静默忽略。如果你想检查是否有未识别配置，可以改用
# extra="forbid" 启动时抛错，或者 extra="allow" 全部保留。


# ===================================================================
# 6. 入口
# ===================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
    uvicorn.run(
        "day69_settings:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )