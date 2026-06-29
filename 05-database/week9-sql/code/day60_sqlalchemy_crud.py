"""
Day 60 - SQLAlchemy CRUD 操作
==============================
使用 Session 完成增删改查（Create, Read, Update, Delete）。

注意事项：
  - 运行后会在当前目录生成 app.db 文件
  - 重复运行会复用已有数据（可删除 app.db 重新开始）

运行方式：python3 day60_sqlalchemy_crud.py
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Session
from datetime import datetime, timezone


# ============================================================
# 模型定义
# ============================================================
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id          = Column(Integer,    primary_key=True, autoincrement=True)
    name        = Column(String(50), nullable=False)
    email       = Column(String(100), nullable=False, unique=True)
    age         = Column(Integer,    default=0)
    created_at  = Column(DateTime,   default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


def print_separator(title):
    """打印分隔标题"""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")


def main():
    # ----------------------------------------------------------
    # 1. 创建引擎（使用文件数据库 app.db，数据持久化）
    # ----------------------------------------------------------
    print("[1] 创建引擎 → 使用文件 app.db")
    engine = create_engine("sqlite:///app.db", echo=False)
    Base.metadata.create_all(engine)

    # ----------------------------------------------------------
    # 2. 创建 Session
    #    Session 是 ORM 的工作单元，所有操作通过它执行
    # ----------------------------------------------------------
    session = Session(engine)

    # ==========================================================
    # CREATE — 创建记录
    # ==========================================================
    print_separator("CREATE — 创建用户")

    user1 = User(name="张三", email="zhangsan@example.com", age=25)
    user2 = User(name="李四", email="lisi@example.com", age=30)
    user3 = User(name="王五", email="wangwu@example.com", age=28)

    # add() — 添加单个；add_all() — 批量添加
    session.add_all([user1, user2, user3])
    session.commit()  # 提交事务，数据写入数据库
    print(f"  已创建 3 位用户")
    print(f"  user1.id = {user1.id}  (提交后自动获得 ID)")
    print(f"  user2.id = {user2.id}")
    print(f"  user3.id = {user3.id}")

    # ==========================================================
    # READ — 读取记录
    # ==========================================================
    print_separator("READ — 查询用户")

    # 查询全部
    all_users = session.query(User).all()
    print(f"[查询全部] 共 {len(all_users)} 位用户:")
    for u in all_users:
        print(f"  {u}")

    # filter_by — 按条件筛选（使用关键字参数）
    users_a = session.query(User).filter_by(name="张三").all()
    print(f"\n[filter_by] name='张三': {users_a}")

    # filter — 更灵活的筛选（支持运算符）
    users_b = session.query(User).filter(User.age >= 28).all()
    print(f"[filter]   age >= 28:")
    for u in users_b:
        print(f"  {u}")

    # get — 按主键查询
    user = session.query(User).get(1)
    print(f"\n[get]      id=1: {user}")

    # first — 取第一条
    first_user = session.query(User).order_by(User.age.desc()).first()
    print(f"[first]    age 最大: {first_user}")

    # ==========================================================
    # UPDATE — 更新记录
    # ==========================================================
    print_separator("UPDATE — 更新用户")

    # 方式一：直接修改对象属性
    user_to_update = session.query(User).filter_by(name="张三").first()
    print(f"  修改前: {user_to_update}")
    user_to_update.age = 26
    session.commit()
    session.refresh(user_to_update)  # 从数据库刷新最新数据
    print(f"  修改后: {user_to_update}")

    # 方式二：批量更新
    session.query(User).filter(User.age == 0).update({"age": 18})
    session.commit()
    print("  已将所有 age=0 的用户更新为 18 岁")

    # ==========================================================
    # DELETE — 删除记录
    # ==========================================================
    print_separator("DELETE — 删除用户")

    user_to_delete = session.query(User).filter_by(name="王五").first()
    print(f"  准备删除: {user_to_delete}")
    session.delete(user_to_delete)
    session.commit()

    # 确认删除
    remaining = session.query(User).count()
    print(f"  删除后剩余用户数: {remaining}")

    # ==========================================================
    # 复杂查询演示
    # ==========================================================
    print_separator("进阶查询")

    # 排序
    users_sorted = session.query(User).order_by(User.age.desc(), User.name.asc()).all()
    print("[order_by] 按年龄降序、姓名升序:")
    for u in users_sorted:
        print(f"  {u}")

    # 计数
    count = session.query(User).count()
    print(f"\n[count]    总用户数: {count}")

    # 限制 & 偏移（分页）
    page = session.query(User).limit(2).offset(0).all()
    print(f"[limit/offset] 第 1 页（每页 2 条）: {page}")

    # ----------------------------------------------------------
    # 3. 关闭 Session
    # ----------------------------------------------------------
    session.close()
    print(f"\n{'=' * 50}")
    print("  CRUD 演示完成！")
    print("  数据已保存在 app.db，下次运行会继续使用。")
    print("  删除 app.db 即可重置数据。")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
