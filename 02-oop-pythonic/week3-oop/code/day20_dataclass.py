"""
day20_dataclass.py — @dataclass 装饰器
=======================================

@dataclass 是 Python 3.7+ 引入的"数据类"装饰器。
它会自动生成 __init__、__repr__、__eq__ 等方法，减少样板代码。

对比手写类与 @dataclass：

    ┌─────────────────────────────────────┬──────────────────────────────────────┐
    │ 手写类（约 15 行）                   │ @dataclass（约 5 行）                │
    ├─────────────────────────────────────┼──────────────────────────────────────┤
    │ class Todo:                         │ @dataclass                          │
    │     def __init__(self, title, done):│ class Todo:                         │
    │         self.title = title          │     title: str                      │
    │         self.done = done            │     done: bool = False              │
    │     def __repr__(self):             │                                      │
    │         return ...                  │     # __init__, __repr__,           │
    │     def __eq__(self, other):        │     # __eq__ 自动生成              │
    │         return ...                  │                                      │
    └─────────────────────────────────────┴──────────────────────────────────────┘
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Todo:
    """
    待办事项类 —— 使用 @dataclass。
    只需要声明类型注解，__init__ / __repr__ / __eq__ 自动生成。
    """

    # 字段：类型注解是必须的
    title: str                    # 必填字段
    done: bool = False            # 有默认值，相当于 init=False
    priority: int = 0             # 优先级（0=普通, 1=重要, 2=紧急）

    # field(default_factory=...) → 每次创建实例时调用工厂函数生成新值
    tags: List[str] = field(default_factory=list)   # 不能用 mutable 做默认值！

    # ── 手写类需要手动实现这些 ──
    # def __init__(self, title, done=False, priority=0, tags=None):
    #     self.title = title
    #     self.done = done
    #     self.priority = priority
    #     self.tags = tags or []
    #
    # def __repr__(self):
    #     return f"Todo(title={self.title!r}, done={self.done!r}, ...)"
    #
    # def __eq__(self, other):
    #     if not isinstance(other, Todo):
    #         return NotImplemented
    #     return (self.title, self.done) == (other.title, other.done)


if __name__ == "__main__":
    print("── @dataclass 演示 ──")

    t1 = Todo("学 Python OOP", priority=2)
    t2 = Todo("写作业", done=True)
    t3 = Todo("学 Python OOP", priority=2)  # 内容和 t1 一样

    # __repr__ 自动生成（比手写更清晰）
    print(f"t1 = {t1}")
    print(f"t2 = {t2}")

    # __eq__ 自动生成
    print(f"\nt1 == t2: {t1 == t2}")  # False
    print(f"t1 == t3: {t1 == t3}")    # True

    # field(default_factory) 演示
    t1.tags.append("重要")
    t1.tags.append("今日")
    print(f"\nt1.tags = {t1.tags}")        # ['重要', '今日']
    print(f"t2.tags = {t2.tags}")          # []（独立的空列表）

    # 字段顺序就是 __init__ 的参数顺序
    t4 = Todo("买咖啡", True, 1, ["生活"])
    print(f"\nt4 = {t4}")