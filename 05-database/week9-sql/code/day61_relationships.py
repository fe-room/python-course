"""
Day 61 - SQLAlchemy 关系映射
=============================
Foreign Key + relationship() + back_populates
实现 User 与 Todo 的一对多关系。

核心概念：
  - ForeignKey：外键约束，指向关联表的主键
  - relationship()：在 Python 层面建立对象导航属性
  - back_populates：双向关联，让两个模型互相引用

运行方式：python3 day61_relationships.py
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship
from datetime import datetime, timezone


# ============================================================
# 模型定义
# ============================================================
class Base(DeclarativeBase):
    pass


class User(Base):
    """用户模型（一方）"""
    __tablename__ = "users"

    id          = Column(Integer,    primary_key=True, autoincrement=True)
    name        = Column(String(50), nullable=False)
    email       = Column(String(100), nullable=False, unique=True)
    created_at  = Column(DateTime,   default=lambda: datetime.now(timezone.utc))

    # 关系属性：User.todos 返回该用户的所有 Todo 列表
    # 通过 back_populates 与 Todo.user 建立双向关联
    todos = relationship("Todo", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}')>"


class Todo(Base):
    """待办事项模型（多方）"""
    __tablename__ = "todos"

    id          = Column(Integer,    primary_key=True, autoincrement=True)
    title       = Column(String(200), nullable=False)
    description = Column(Text,       default="")
    completed   = Column(Boolean,    default=False)
    created_at  = Column(DateTime,   default=lambda: datetime.now(timezone.utc))

    # 外键列：指向 users.id
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 关系属性：Todo.user 返回该待办所属的 User 对象
    user = relationship("User", back_populates="todos")

    def __repr__(self):
        status = "✓" if self.completed else "○"
        return f"<Todo(id={self.id}, title='{self.title}', {status})>"


def print_relations_demo():
    """演示关系如何工作"""
    print("=" * 55)
    print("User ↔ Todo 关系模型")
    print("=" * 55)
    print("""
  User（一方）              Todo（多方）
  ┌────────────┐           ┌──────────────────┐
  │ id         │◄──────────│ user_id (FK)     │
  │ name       │     1    N│ title             │
  │ email      │           │ completed         │
  │ todos ─────┼───rel───►│ user ───rel──►    │
  └────────────┘           └──────────────────┘

  user.todos  → 该用户的所有待办
  todo.user   → 该待办所属的用户
    """)


def main():
    print_relations_demo()

    # ----------------------------------------------------------
    # 1. 创建引擎 & 表
    # ----------------------------------------------------------
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    session = Session(engine)

    # ----------------------------------------------------------
    # 2. 创建用户和待办
    # ----------------------------------------------------------
    print("[1] 创建用户及待办事项")

    # 创建用户
    zhang = User(name="张三", email="zhang@example.com")
    li = User(name="李四", email="li@example.com")

    # 创建待办并关联用户
    todo1 = Todo(title="完成 Python 作业", description="第 61 天关系映射练习", user=zhang)
    todo2 = Todo(title="买菜",              description="鸡蛋、牛奶、面包",     user=zhang)
    todo3 = Todo(title="健身",              description="跑步 30 分钟",        user=zhang)
    todo4 = Todo(title="阅读《设计模式》",   description="第 3 章",            user=li)
    todo5 = Todo(title="写周报",            description="本周工作总结",        user=li)

    session.add_all([zhang, li, todo1, todo2, todo3, todo4, todo5])
    session.commit()
    print("  已创建 2 位用户，5 条待办事项\n")

    # ----------------------------------------------------------
    # 3. 正向导航：User → Todo
    #    user.todos 返回该用户的所有 Todo 对象列表
    # ----------------------------------------------------------
    print("[2] 正向导航：user.todos")

    user = session.query(User).filter_by(name="张三").first()
    print(f"  用户: {user.name}")
    print(f"  待办列表 ({len(user.todos)} 项):")
    for t in user.todos:
        status = "已完成" if t.completed else "待完成"
        print(f"    [{status}] {t.title} — {t.description}")

    print()

    # ----------------------------------------------------------
    # 4. 反向导航：Todo → User
    #    todo.user 返回该待办所属的 User 对象
    # ----------------------------------------------------------
    print("[3] 反向导航：todo.user")

    todo = session.query(Todo).filter_by(title="买菜").first()
    print(f"  待办: '{todo.title}'")
    print(f"  所属用户: {todo.user.name} ({todo.user.email})")
    print()

    # ----------------------------------------------------------
    # 5. 级联操作（cascade）
    #    删除用户时，其所有待办也会被自动删除
    # ----------------------------------------------------------
    print("[4] 级联删除演示")

    # 先统计删除前的数量
    total_todos_before = session.query(Todo).count()
    print(f"  删除前待办总数: {total_todos_before}")

    # 删除李四（其待办也会被自动删除）
    li_user = session.query(User).filter_by(name="李四").first()
    session.delete(li_user)
    session.commit()

    total_todos_after = session.query(Todo).count()
    print(f"  删除李四后的待办数: {total_todos_after}")
    print(f"  （级联删除自动清除了李四的待办）\n")

    # ----------------------------------------------------------
    # 6. 使用关联添加新待办
    # ----------------------------------------------------------
    print("[5] 通过关系添加新待办")

    zhang_user = session.query(User).filter_by(name="张三").first()
    new_todo = Todo(title="学习 SQLAlchemy 关系", description="一对多、多对多")
    zhang_user.todos.append(new_todo)  # 通过关系列表添加
    session.commit()
    print(f"  张三现在有 {len(zhang_user.todos)} 条待办")
    for t in zhang_user.todos:
        print(f"    - {t.title}")

    # ----------------------------------------------------------
    # 6. 关闭
    # ----------------------------------------------------------
    session.close()
    print(f"\n{'=' * 55}")
    print("  关系映射演示完成！")
    print("  关键点：ForeignKey + relationship + back_populates")
    print("  cascade='all, delete-orphan' 实现级联删除")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    main()
