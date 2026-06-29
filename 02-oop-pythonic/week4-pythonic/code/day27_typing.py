"""
day27_typing.py — 类型注解（Type Hints）入门
==============================================
Python 3.5+ 支持可选的类型注解，配合 mypy 可以做静态类型检查。
注意：类型注解不会影响运行，只是给开发者和工具看的"文档"。

运行 mypy 检查：
    pip install mypy
    mypy day27_typing.py          # 会报告类型不匹配的地方
"""

from typing import Optional, Union, List, Dict, Tuple


# ── 1. 基本类型注解 ───────────────────────────────────────

def greet(name: str, age: int) -> str:
    """
    参数和返回值都加了类型注解。
    name: str    — name 必须是字符串
    age: int     — age 必须是整数
    -> str       — 返回值必须是字符串
    """
    return f"你好，我叫 {name}，今年 {age} 岁。"


# ── 2. Optional：可能为 None ──────────────────────────────

def find_user(user_id: int) -> Optional[str]:
    """
    Optional[str] 等价于 Union[str, None]。
    表示返回值可能是一个字符串，也可能是 None。
    """
    database = {1: "Alice", 2: "Bob", 3: "Charlie"}
    return database.get(user_id)     # 找不到时返回 None


# ── 3. Union：联合类型 ────────────────────────────────────

def parse_input(data: Union[str, int, float]) -> str:
    """
    Union[str, int, float] 表示 data 可以是 str、int 或 float 中的任意一种。
    Python 3.10+ 可以简写成 str | int | float。
    """
    return f"解析结果: {data}"


# ── 4. List、Dict、Tuple：容器类型 ────────────────────────

def process_scores(scores: List[int]) -> Dict[str, float]:
    """
    List[int]      — 元素为 int 的列表
    Dict[str, float] — key 是 str、value 是 float 的字典
    Tuple[int, str]  — 固定长度的元组
    """
    total = sum(scores)
    count = len(scores)
    return {
        "总和": float(total),
        "平均": total / count if count > 0 else 0.0,
    }


def split_name(full_name: str) -> Tuple[str, str]:
    """将全名拆成 (名, 姓)，返回 Tuple[str, str]"""
    parts = full_name.split()
    if len(parts) >= 2:
        return (parts[0], parts[1])
    return (full_name, "")


# ── 5. 复杂一点的例子：带注解的类 ─────────────────────────

class Student:
    """学生类，展示类属性的类型注解"""

    def __init__(self, name: str, scores: List[int]) -> None:
        self.name: str = name
        self.scores: List[int] = scores

    def average(self) -> float:
        """计算平均分"""
        return sum(self.scores) / len(self.scores) if self.scores else 0.0

    def report(self) -> Dict[str, Union[str, float]]:
        """返回成绩报告"""
        return {
            "name": self.name,
            "average": self.average(),
        }


# ── 演示入口 ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("1. 基本类型注解")
    print("=" * 50)
    print(greet("小明", 18))

    print("\n" + "=" * 50)
    print("2. Optional 演示")
    print("=" * 50)
    print(f"找到用户 1: {find_user(1)}")
    print(f"找到用户 5: {find_user(5)}")

    print("\n" + "=" * 50)
    print("3. Union 演示")
    print("=" * 50)
    print(parse_input("hello"))
    print(parse_input(42))
    print(parse_input(3.14))

    print("\n" + "=" * 50)
    print("4. List / Dict / Tuple 演示")
    print("=" * 50)
    scores = [85, 92, 78, 90, 88]
    result = process_scores(scores)
    print(f"分数: {scores}")
    print(f"统计: {result}")
    print(f"拆分姓名 '张三丰': {split_name('张三丰')}")

    print("\n" + "=" * 50)
    print("5. 带类型注解的类")
    print("=" * 50)
    s = Student("Alice", [95, 88, 92])
    print(f"学生: {s.name}")
    print(f"平均分: {s.average()}")
    print(f"报告: {s.report()}")

    # ── 关于 mypy 的说明 ──────────────────────────────────
    print("\n" + "=" * 50)
    print("关于 mypy 的说明")
    print("=" * 50)
    print("""
    类型注解只是"提示"，不会影响运行时的行为。
    要真正做类型检查，需要安装 mypy：

        pip install mypy
        mypy day27_typing.py

    mypy 会检查类型是否匹配。例如下面这行代码：
        result: str = greet("小明", "18")   # 第 2 个参数应该是 int，但传了 str
    如果你取消注释并运行 mypy，它就会报错。但直接运行 Python 不会报错。
    """)
