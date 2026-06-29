"""
day18_inherit.py — 继承与 super()
===================================

继承（Inheritance）是 OOP 三大特性之一。
子类可以：
    1. 继承父类的所有方法和属性
    2. 覆写（override）父类的方法
    3. 通过 super() 调用父类的方法

对比 JS 的继承：
    // JS
    class AdminUser extends User {
        constructor(name, email, role) {
            super(name, email);        // 调用父类构造
            this.role = role;
        }
    }
"""

import datetime


class User:
    """父类（基类）：普通用户。"""

    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email
        self.registered_at = datetime.datetime.now()

    def greet(self) -> str:
        return f"Hi, I'm {self.name}"

    def show_info(self) -> str:
        return f"User({self.name}, {self.email})"


class AdminUser(User):
    """
    子类：管理员用户。
    User 是父类（Parent），AdminUser 是子类（Child）。
    """

    def __init__(self, name: str, email: str, permissions: list[str] | None = None) -> None:
        # super() → 调用父类的 __init__，避免重复写 name/email 的赋值
        super().__init__(name, email)
        # 子类特有的属性
        self.permissions = permissions or ["read"]

    # ── 覆写父类方法 ──────────────────────────────────────────
    def greet(self) -> str:
        """覆写 greet()，管理员有专属问候。"""
        return f"Hello, I'm admin {self.name}"

    # ── 子类新增方法 ──────────────────────────────────────────
    def has_permission(self, perm: str) -> bool:
        """检查是否拥有某个权限。"""
        return perm in self.permissions

    def show_info(self) -> str:
        """覆写 show_info()，同时通过 super() 复用父类逻辑。"""
        base_info = super().show_info()
        return f"{base_info} | permissions={self.permissions}"


if __name__ == "__main__":
    print("── 父类 User ──")
    u = User("小明", "xiaoming@example.com")
    print(u.greet())
    print(u.show_info())

    print("\n── 子类 AdminUser ──")
    admin = AdminUser("管理员", "admin@example.com", ["read", "write", "delete"])
    print(admin.greet())               # 覆写后的方法
    print(admin.show_info())           # 覆写 + super()
    print(f"has delete? {admin.has_permission('delete')}")   # True
    print(f"has export?  {admin.has_permission('export')}")  # False

    # 子类也拥有父类的属性
    print(f"\n注册时间: {admin.registered_at}")

    # isinstance 检查
    print(f"\nisinstance(admin, User) = {isinstance(admin, User)}")       # True
    print(f"isinstance(admin, AdminUser) = {isinstance(admin, AdminUser)}")  # True
    print(f"isinstance(u, AdminUser) = {isinstance(u, AdminUser)}")         # False