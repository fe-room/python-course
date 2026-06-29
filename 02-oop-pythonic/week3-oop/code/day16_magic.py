"""
day16_magic.py — 魔术方法（Magic Methods）
==========================================

魔术方法（也叫 dunder methods）是 Python 中以双下划线开头和结尾的特殊方法。
它们让自定义类表现得像内置类型一样。

常见魔术方法：
    __str__   → str(obj) / print(obj)，面向普通用户的可读字符串
    __repr__  → repr(obj)，面向开发者的"官方"字符串表示
    __eq__    → obj1 == obj2，相等判断
    __lt__    → obj1 < obj2，小于比较（用于排序）
"""


class User:
    """用户类，演示常见的魔术方法。"""

    def __init__(self, name: str, email: str, age: int = 0) -> None:
        self.name = name
        self.email = email
        self.age = age

    # ── __str__ ──────────────────────────────────────────────
    def __str__(self) -> str:
        """给用户看的字符串。print() 和 str() 会调用它。"""
        return f"👤 {self.name} <{self.email}>"

    # ── __repr__ ──────────────────────────────────────────────
    def __repr__(self) -> str:
        """给开发者看的字符串。调试时非常有用。"""
        return f"User(name={self.name!r}, email={self.email!r}, age={self.age!r})"

    # ── __eq__ ────────────────────────────────────────────────
    def __eq__(self, other: object) -> bool:
        """定义 == 的行为。"""
        if not isinstance(other, User):
            return NotImplemented
        return self.name == other.name and self.email == other.email

    # ── __lt__ ────────────────────────────────────────────────
    def __lt__(self, other: "User") -> bool:
        """定义 < 的行为。用于 sorted() 排序。"""
        if not isinstance(other, User):
            return NotImplemented
        return self.name < other.name


if __name__ == "__main__":
    u1 = User("小明", "xiaoming@example.com", 25)
    u2 = User("小红", "xiaohong@example.com", 23)
    u3 = User("小明", "xiaoming@example.com", 25)  # 和 u1 内容相同

    # __str__ 演示
    print("── __str__ 演示 ──")
    print(str(u1))
    print(u1)  # print() 内部调用 str()

    # __repr__ 演示
    print("\n── __repr__ 演示 ──")
    print(repr(u1))

    # __eq__ 演示
    print("\n── __eq__ 演示 ──")
    print(f"u1 == u2: {u1 == u2}")  # False（名字不同）
    print(f"u1 == u3: {u1 == u3}")  # True（名字和 email 都相同）

    # __lt__ 演示（排序）
    print("\n── __lt__ 演示（排序）──")
    users = [u1, u2]
    for u in sorted(users):
        print(f"  {u.name}")
    # 输出: 小红 < 小明（按拼音字母排序）