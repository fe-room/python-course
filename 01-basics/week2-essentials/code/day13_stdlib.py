"""
day13_stdlib.py — Python 标准库常用模块
=========================================
知识点：
  1. datetime — 日期时间处理
  2. random — 随机数生成
  3. math — 数学函数
  4. 实战：随机每日名言 CLI
"""

from datetime import datetime, date, timedelta
import random
import math
from pathlib import Path

HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# 1. datetime 模块
# ---------------------------------------------------------------------------
print("=" * 50)
print("1. datetime 模块 — 日期时间处理")
print("=" * 50)

# 获取当前日期时间
now = datetime.now()
print(f"当前时间: {now}")
print(f"  年: {now.year}, 月: {now.month}, 日: {now.day}")
print(f"  时: {now.hour}, 分: {now.minute}, 秒: {now.second}")
print(f"  星期: {now.weekday()} (0=周一, 6=周日)")

# 格式化日期时间
print(f"\n格式化的日期: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"中文格式: {now.strftime('%Y年%m月%d日 %H:%M')}")

# 字符串 -> datetime
date_str = "2024-12-25 10:30:00"
parsed = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
print(f"\n解析字符串: '{date_str}' -> {parsed}")

# 日期计算 (timedelta)
today = date.today()
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)
print(f"\n今天: {today}")
print(f"明天: {tomorrow}")
print(f"昨天: {yesterday}")

# 计算两个日期之间的天数
d1 = date(2025, 1, 1)
d2 = date(2025, 12, 25)
delta = d2 - d1
print(f"\n{d2} - {d1} = {delta.days} 天")

# ---------------------------------------------------------------------------
# 2. random 模块
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("2. random 模块 — 随机数")
print("=" * 50)

# 随机浮点数 [0.0, 1.0)
print(f"random(): {random.random():.4f}")

# 随机整数 [a, b] (包含两端)
print(f"randint(1, 100): {random.randint(1, 100)}")

# 从列表中随机选一个
fruits = ["苹果", "香蕉", "橘子", "西瓜", "草莓"]
print(f"choice({fruits}): {random.choice(fruits)}")

# 从列表中随机选 k 个（不重复）
print(f"sample({fruits}, 3): {random.sample(fruits, 3)}")

# 打乱列表（原地修改）
cards = list(range(1, 11))
random.shuffle(cards)
print(f"shuffle 后: {cards}")

# 随机范围步进值
print(f"randrange(0, 100, 10): {random.randrange(0, 100, 10)}")

# ---------------------------------------------------------------------------
# 3. math 模块
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("3. math 模块 — 数学函数")
print("=" * 50)

numbers = [16, 25, 100, 2, 3.14, -5]

for n in numbers:
    sqrt_val = math.sqrt(n) if n >= 0 else "N/A"
    print(f"  sqrt({n:6}) = {sqrt_val}")

print(f"\npi = {math.pi:.6f}")
print(f"e  = {math.e:.6f}")
print(f"ceil(3.14)  = {math.ceil(3.14)}")    # 向上取整
print(f"floor(3.14) = {math.floor(3.14)}")   # 向下取整
print(f"sin(pi/2)   = {math.sin(math.pi / 2):.1f}")
print(f"pow(2, 10)  = {math.pow(2, 10)}")    # 2^10

# ---------------------------------------------------------------------------
# 4. 练习题：随机每日名言 CLI
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("练习题：随机每日名言 CLI")
print("=" * 50)
"""
请实现函数 daily_quote(quotes=None)：
  - 如果 quotes 为 None，使用内置的名言列表
  - 从名言列表中随机选一条
  - 根据今天是星期几，添加不同的问候语前缀
    周一: "新的一周，加油！"
    周末: "周末愉快！"
    其他: "今天也要元气满满！"
  - 返回格式化的字符串："[问候语] 名言 —— 作者"

例如：
  "[新的一周，加油！] 千里之行，始于足下。 —— 老子"
"""

# ---------- 你的代码从这里开始 ----------

def daily_quote(quotes=None):
    """
    根据当天是星期几，返回一条随机名言。
    quotes: 列表，每个元素是 (名言, 作者) 的元组
    """
    if quotes is None:
        quotes = [
            ("千里之行，始于足下", "老子"),
            ("学而不思则罔，思而不学则殆", "孔子"),
            ("生活就像一盒巧克力，你永远不知道下一颗是什么味道", "阿甘正传"),
            (" stay hungry, stay foolish", "Steve Jobs"),
            ("要么读书，要么旅行，身体和灵魂总有一个在路上", "佚名"),
            ("成功是 99% 的汗水加 1% 的灵感", "爱迪生"),
            ("人生苦短，我用 Python", "Python 社区"),
        ]

    # 获取今天是星期几 (0=周一, 6=周日)
    weekday = datetime.now().weekday()

    if weekday == 0:
        greeting = "新的一周，加油！"
    elif weekday >= 5:
        greeting = "周末愉快！"
    else:
        greeting = "今天也要元气满满！"

    quote, author = random.choice(quotes)
    return f"[{greeting}] {quote} —— {author}"


# ---------- 测试 ----------

def test_daily_quote():
    print("今日名言 (每次运行可能不同):")
    print(daily_quote())

    # 用自定义名言列表测试
    custom = [
        ("Practice makes perfect", "Unknown"),
        ("Hello, World!", "Programmer"),
    ]
    print("\n自定义名言列表测试:")
    print(daily_quote(custom))

    # 验证返回值格式
    result = daily_quote()
    assert "[" in result and "]" in result, "应该包含问候语"
    assert "——" in result, "应该包含作者分隔符"
    print(f"格式验证通过: {result}")

    print("\n测试全部通过！")

if __name__ == "__main__":
    test_daily_quote()
    print("\n标准库演示完成。")