"""
day17_property.py — @property 装饰器
=====================================

@property 可以把一个方法变成"属性"来访问（不需要加括号）。
适合：
    1. 需要计算才能得到的属性（如：is_new）
    2. 从其他属性派生的值（如：email_domain）
    3. 需要只读保护的属性

对比 JS 的 getter：
    // JS
    class User {
        get isNew() { return ... }
    }
    // 访问时：user.isNew（没有括号）
"""

import datetime


class User:
    """用户类，演示 @property 的用法。"""

    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email
        self.registered_at = datetime.datetime.now()

    # ── @property → 像属性一样访问，不加括号 ────────────────
    @property
    def is_new(self) -> bool:
        """判断用户是否是新人：注册时间在 7 天以内。"""
        days = (datetime.datetime.now() - self.registered_at).days
        return days < 7

    @property
    def email_domain(self) -> str:
        """从 email 中提取域名部分。"""
        return self.email.split("@")[-1]

    # 只读属性（不写 setter，外部就无法赋值）
    @property
    def registered_date(self) -> str:
        """返回格式化的注册日期（只读）。"""
        return self.registered_at.strftime("%Y-%m-%d %H:%M")


if __name__ == "__main__":
    u = User("小明", "xiaoming@example.com")

    # 像访问属性一样使用，不是方法调用
    print("── @property 演示 ──")
    print(f"is_new       = {u.is_new}")            # True（刚注册）
    print(f"email_domain = {u.email_domain}")      # example.com
    print(f"registered   = {u.registered_date}")

    # 下面的代码会报错，因为 registered_date 没有 setter
    # u.registered_date = "2025-01-01"  # AttributeError!

    print("\n── 对比：普通方法调用 ──")
    # 没有 @property 的话需要加括号
    print(f"普通方法: {u.email_domain}")