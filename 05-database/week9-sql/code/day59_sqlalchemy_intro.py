"""
Day 59 - SQLAlchemy 入门：ORM 基础
===================================
安装依赖：pip install sqlalchemy

SQLAlchemy 是 Python 最流行的 ORM（对象关系映射）库。
ORM 让我们用 Python 对象操作数据库，而不需要手写 SQL。

核心概念：
  - DeclarativeBase：声明式基类，所有模型继承它
  - Column：定义表字段
  - create_engine：创建数据库引擎
  - Base.metadata.create_all()：根据模型创建表

运行方式：python3 day59_sqlalchemy_intro.py
"""

# 导入 SQLAlchemy 核心组件
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone


# ============================================================
# 第一步：定义基类
# SQLAlchemy 2.0 使用 DeclarativeBase（旧版是 declarative_base()）
# ============================================================
class Base(DeclarativeBase):
    """所有模型类的基类"""
    pass


# ============================================================
# 第二步：定义 User 模型（对应数据库中的 users 表）
# ============================================================
class User(Base):
    """
    用户模型

    类名 User 默认对应表名 users（自动复数化 + 小写）
    也可以通过 __tablename__ 自定义表名
    """
    __tablename__ = "users"  # 数据库中实际的表名

    # --- 字段定义 ---
    id          = Column(Integer,    primary_key=True, autoincrement=True)
    name        = Column(String(50), nullable=False, comment="用户名")
    email       = Column(String(100), nullable=False, unique=True, comment="邮箱")
    age         = Column(Integer,    default=0, comment="年龄")
    bio         = Column(Text,       default="", comment="个人简介")
    created_at  = Column(DateTime,   default=lambda: datetime.now(timezone.utc), comment="创建时间")

    def __repr__(self):
        """方便调试的字符串表示"""
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


def main():
    print("=" * 55)
    print("SQLAlchemy ORM 入门演示")
    print("=" * 55)

    # ============================================================
    # 第三步：创建数据库引擎
    # echo=True 会打印所有执行的 SQL 语句，方便调试
    # ============================================================
    print("\n[1] 创建引擎 (SQLite :memory:)")
    engine = create_engine("sqlite:///:memory:", echo=True)

    # ============================================================
    # 第四步：创建表
    # Base.metadata.create_all() 扫描所有继承 Base 的模型，生成 CREATE TABLE
    # ============================================================
    print("\n[2] 根据模型定义创建表...")
    Base.metadata.create_all(engine)

    # 查看映射信息
    print(f"\n[3] 表结构信息")
    user_table = User.__table__
    print(f"   表名: {user_table.name}")
    print(f"   字段:")
    for col in user_table.columns:
        print(f"     - {col.name:12} {col.type!s:15} nullable={col.nullable}")

    # ============================================================
    # 第五步：检查数据库中的表
    # ============================================================
    inspector = engine.dialect.has_table
    print(f"\n[4] 表 'users' 是否存在: {inspector(engine.connect(), 'users')}")

    print(f"\n{'=' * 55}")
    print("模型类结构一览：")
    print(f"  class User(Base):")
    print(f"    __tablename__ = 'users'")
    print(f"    id        = Column(Integer,    Primary Key)")
    print(f"    name      = Column(String(50),   NOT NULL)")
    print(f"    email     = Column(String(100),  NOT NULL, UNIQUE)")
    print(f"    age       = Column(Integer,      default=0)")
    print(f"    bio       = Column(Text,         default='')")
    print(f"    created_at= Column(DateTime,     auto now)")
    print(f"{'=' * 55}")
    print("下一步：使用 Session 执行 CRUD 操作 → day60_sqlalchemy_crud.py")
    print("=" * 55)


if __name__ == "__main__":
    main()
