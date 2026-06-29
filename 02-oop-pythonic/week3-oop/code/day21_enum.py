"""
day21_enum.py — Enum 枚举 + __post_init__
==========================================

Enum（枚举）用来表示一组固定的常量值，比用字符串更安全、更清晰。

    # 不推荐：魔法字符串
    if status == "pending": ...      # 拼错了也不会报错！

    # 推荐：枚举
    if status is Status.PENDING: ... # 类型安全，IDE 自动补全

__post_init__ 是 @dataclass 提供的钩子方法。
__init__ 执行完后会自动调用它，适合做校验或派生字段。
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import List


class Status(Enum):
    """任务状态枚举。"""
    # auto() 自动赋值为 1, 2, 3 ...
    PENDING = auto()    # 待办   (PENDING = 1)
    DONE = auto()       # 已完成 (DONE = 2)
    ARCHIVED = auto()   # 已归档 (ARCHIVED = 3)

    # 也可以手动赋值：
    # PENDING = "pending"
    # DONE = "done"
    # ARCHIVED = "archived"

    def __str__(self) -> str:
        """让 print(status) 显示中文。"""
        labels = {
            Status.PENDING: "⏳ 待办",
            Status.DONE: "✅ 已完成",
            Status.ARCHIVED: "📦 已归档",
        }
        return labels[self]


@dataclass
class Todo:
    """待办事项 —— 使用 Enum 做状态管理。"""

    title: str
    status: Status = Status.PENDING
    tags: List[str] = None
    created_at: datetime = None

    # ── __post_init__ ─────────────────────────────────────────
    def __post_init__(self) -> None:
        """
        __init__ 执行完后自动调用。
        适合做：
            1. 字段校验
            2. 为 None 的字段设置默认值
            3. 派生/计算字段
        """
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()

        # 校验：已完成或已归档的任务必须有标签（示例规则）
        if self.status in (Status.DONE, Status.ARCHIVED) and not self.tags:
            raise ValueError(f"任务 '{self.title}' 状态为 {self.status}，但缺少标签！")

    def complete(self) -> None:
        """标记为已完成。"""
        self.status = Status.DONE

    def archive(self) -> None:
        """标记为已归档。"""
        self.status = Status.ARCHIVED


if __name__ == "__main__":
    print("── Enum 演示 ──")

    # 枚举成员是单例（唯一实例）
    print(f"Status.PENDING = {Status.PENDING}")       # Status.PENDING
    print(f"Status.PENDING.name = {Status.PENDING.name}")   # PENDING
    print(f"Status.PENDING.value = {Status.PENDING.value}")  # 1

    # 遍历枚举
    print("\n所有状态:")
    for s in Status:
        print(f"  {s.name} = {s.value} → {s}")

    print("\n── Todo 演示 ──")

    # 创建待办任务
    todo1 = Todo("学习 Python Enum")
    print(f"todo1: {todo1.title} | {todo1.status}")

    # 改变状态
    todo1.complete()
    todo1.tags.append("python")
    print(f"todo1: {todo1.title} | {todo1.status}")

    todo1.archive()
    print(f"todo1: {todo1.title} | {todo1.status}")

    # 创建已完成的任务（需要标签）
    todo2 = Todo("写代码", status=Status.DONE, tags=["编程"])
    print(f"\ntodo2: {todo2.title} | {todo2.status} | tags={todo2.tags}")

    # 状态比较
    print(f"\ntodo1.status is Status.ARCHIVED: {todo1.status is Status.ARCHIVED}")  # True