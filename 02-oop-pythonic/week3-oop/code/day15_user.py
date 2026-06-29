"""
day15_user.py — 最基本的类与实例方法
=====================================

对比 JavaScript 的构造函数：
    // JS 写法
    class User {
        constructor(name, email) {
            this.name = name;
            this.email = email;
        }
        greet() {
            return `Hi, I'm ${this.name}`;
        }
    }

Python 的 __init__ 相当于 JS 的 constructor。
self 相当于 JS 的 this（但 self 是显式参数）。
"""

import datetime


class User:
    """用户类，演示最基本的类定义与实例方法。"""

    def __init__(self, name: str, email: str) -> None:
        """构造方法，相当于 JS 的 constructor。"""
        self.name = name
        self.email = email
        self.registered_at = datetime.datetime.now()

    def greet(self) -> str:
        """实例方法：返回问候语。第一个参数永远是 self。"""
        return f"Hi, I'm {self.name}"

    def show_info(self) -> str:
        """实例方法：返回用户信息字符串。"""
        return f"User({self.name}, {self.email})"


if __name__ == "__main__":
    # ---- 演示 ----
    u1 = User("小明", "xiaoming@example.com")
    u2 = User("小红", "xiaohong@example.com")

    print(u1.greet())           # Hi, I'm 小明
    print(u2.greet())           # Hi, I'm 小红
    print(u1.show_info())       # User(小明, xiaoming@example.com)
    print(u2.show_info())       # User(小红, xiaohong@example.com)

    # Python 中也可以直接访问属性（没有 JS 的 # 私有约定）
    print(f"name = {u1.name}, email = {u1.email}")