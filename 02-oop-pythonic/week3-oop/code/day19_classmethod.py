"""
day19_classmethod.py — @classmethod 与 @staticmethod
=====================================================

两种特殊方法的区别：

    ╔══════════════════╤═══════════════════╤═══════════════════╗
    ║                  │ @classmethod      │ @staticmethod     ║
    ╠══════════════════╪═══════════════════╪═══════════════════╣
    ║ 第一个参数       │ cls（类本身）     │ 无特殊参数        ║
    ║ 能否访问类属性   │ 可以              │ 不可以            ║
    ║ 能否被继承覆写   │ 可以（多态）      │ 不可以            ║
    ║ 典型用途         │ 工厂方法          │ 工具/辅助函数     ║
    ╚══════════════════╧═══════════════════╧═══════════════════╝

对比 JS：
    JS 的 static 方法同时涵盖了 classmethod 和 staticmethod 的用途。
    Python 分得更细。
"""

import re


class User:
    """用户类，演示 @classmethod 和 @staticmethod。"""

    # 类属性（所有实例共享）
    # 注释：类属性在 JS 中是静态属性
    default_domain = "example.com"

    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email

    # ── @classmethod ──────────────────────────────────────────
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """
        工厂方法：从字典创建 User 实例。
        cls 是类本身（在这里就是 User），所以即使被子类调用也能正确创建。
        """
        return cls(name=data["name"], email=data["email"])

    @classmethod
    def create_default(cls, name: str) -> "User":
        """工厂方法：使用默认域名创建用户。"""
        return cls(name=name, email=f"{name}@{cls.default_domain}")

    # ── @staticmethod ─────────────────────────────────────────
    @staticmethod
    def validate_email(email: str) -> bool:
        """静态方法：验证 email 格式是否合法。不需要 cls 或 self。"""
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

    @staticmethod
    def sanitize_name(name: str) -> str:
        """静态方法：清洗用户名（去掉首尾空格）。"""
        return name.strip().title()


if __name__ == "__main__":
    # ── @staticmethod 演示 ──
    print("── @staticmethod 演示 ──")
    print(f"validate_email('abc@xyz.com'): {User.validate_email('abc@xyz.com')}")       # True
    print(f"validate_email('not-email'):   {User.validate_email('not-email')}")         # False
    print(f"sanitize_name('  xiao ming '): '{User.sanitize_name('  xiao ming ')}'")     # 'Xiao Ming'

    # ── @classmethod 演示 ──
    print("\n── @classmethod 演示 ──")

    # 从字典创建
    data = {"name": "小明", "email": "xiaoming@example.com"}
    u1 = User.from_dict(data)
    print(f"from_dict → {u1.name}, {u1.email}")

    # 使用默认域名创建
    u2 = User.create_default("xiaohong")
    print(f"create_default → {u2.name}, {u2.email}")  # xiaohong@example.com

    # 注意：实例也可以调用类方法和静态方法（但不推荐）
    print(f"\n实例调用静态方法: {u1.validate_email(u1.email)}")  # True