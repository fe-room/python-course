"""
day10_errors.py — 异常处理与自定义异常
========================================
知识点：
  1. try / except / else / finally 完整结构
  2. 捕获多种异常类型
  3. 自定义异常类
  4. 实战：安全读取 CSV
"""

import csv
from pathlib import Path

HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# 1. try / except / else / finally 完整结构
# ---------------------------------------------------------------------------
print("=" * 50)
print("1. try / except / else / finally 完整结构")
print("=" * 50)
"""
完整流程：
  try:     可能出错的代码
  except:  出错时执行
  else:    没出错时执行
  finally: 不管是否出错都会执行（善后清理）
"""

def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print(f"  错误: 不能除以零 ({a} / {b})")
    else:
        print(f"  {a} / {b} = {result}")
        return result
    finally:
        print(f"   finally: 这行无论如何都会打印")

print("调用 divide(10, 2):")
divide(10, 2)

print("\n调用 divide(10, 0):")
divide(10, 0)

# ---------------------------------------------------------------------------
# 2. 捕获多种异常类型
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("2. 捕获多种异常类型")
print("=" * 50)

def risky_operation(value, index):
    """一个可能触发多种异常的函数"""
    try:
        # 可能触发 TypeError (value 不支持索引)
        item = value[index]
        # 可能触发 ZeroDivisionError
        result = 100 / item
        # 可能触发 NameError (访问不存在的变量)
        print(f"结果: {result}")
    except TypeError as e:
        print(f"  TypeError: {e} (value 可能不支持索引)")
    except ZeroDivisionError as e:
        print(f"  ZeroDivisionError: {e}")
    except Exception as e:
        # 捕获所有其他异常（兜底）
        print(f"  其他异常 ({type(e).__name__}): {e}")
    else:
        print(f"  操作成功完成！")
    finally:
        print(f"  清理工作...")

print("调用 risky_operation([1, 2, 3], 0):")
risky_operation([1, 2, 3], 0)

print("\n调用 risky_operation([1, 0, 3], 1):")
risky_operation([1, 0, 3], 1)

print("\n调用 risky_operation(42, 0):")
risky_operation(42, 0)

print("\n调用 risky_operation([1, 2], 10):")
risky_operation([1, 2], 10)

# ---------------------------------------------------------------------------
# 3. 自定义异常类
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("3. 自定义异常类")
print("=" * 50)


class ValidationError(Exception):
    """数据校验失败时抛出的异常"""
    pass


class NegativeValueError(ValidationError):
    """值为负数时抛出的异常"""
    pass


class OutOfRangeError(ValidationError):
    """值超出允许范围时抛出的异常"""
    def __init__(self, value, min_val, max_val):
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        super().__init__(f"值 {value} 不在 [{min_val}, {max_val}] 范围内")


def validate_score(score):
    """校验分数，如果非法则抛出自定义异常"""
    if not isinstance(score, (int, float)):
        raise ValidationError(f"分数必须是数字，收到 {type(score).__name__}")
    if score < 0:
        raise NegativeValueError(f"分数不能为负数: {score}")
    if score > 100:
        raise OutOfRangeError(score, 0, 100)
    return True


print("测试 validate_score:")
test_values = [85, -5, 150, "abc"]

for v in test_values:
    try:
        validate_score(v)
        print(f"  {v} -> 有效")
    except NegativeValueError as e:
        print(f"  {v} -> NegativeValueError: {e}")
    except OutOfRangeError as e:
        print(f"  {v} -> OutOfRangeError: {e}")
    except ValidationError as e:
        print(f"  {v} -> ValidationError: {e}")

# ---------------------------------------------------------------------------
# 4. 练习题：safe_read_csv 带错误处理
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("练习题：safe_read_csv 带错误处理")
print("=" * 50)
"""
请实现函数 safe_read_csv(filepath, required_columns)：
  - filepath: 字符串或 Path，CSV 文件路径
  - required_columns: 列表，CSV 必须包含的列名
  - 需要处理以下异常：
      FileNotFoundError -> 打印 "文件不存在" 并返回空列表
      csv.Error -> 打印 "CSV 格式错误" 并返回空列表
      KeyError -> 打印 f"缺少列: {列名}" 并返回空列表
  - 正常时返回列表，每个元素是字典（一行数据）
"""

# ---------- 你的代码从这里开始 ----------

def safe_read_csv(filepath, required_columns):
    """
    安全读取 CSV 文件，处理常见异常。
    返回字典列表，出错时返回空列表。
    """
    try:
        with open(filepath, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            # 检查必需列是否存在
            if reader.fieldnames is None:
                print("错误: 文件为空或无法读取列名")
                return []

            for col in required_columns:
                if col not in reader.fieldnames:
                    raise KeyError(f"缺少列: {col}")

            # 读取所有行
            result = []
            for row in reader:
                result.append(row)
            return result

    except FileNotFoundError:
        print(f"文件不存在: {filepath}")
        return []
    except csv.Error as e:
        print(f"CSV 格式错误: {e}")
        return []
    except KeyError as e:
        print(f"KeyError: {e}")
        return []

# ---------- 测试 ----------

def test_safe_read_csv():
    test_csv = HERE / "_test_grades.csv"

    # 准备测试数据
    with open(test_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "chinese", "math"])
        writer.writerow(["Alice", 90, 85])
        writer.writerow(["Bob", 70, 60])

    # 测试 1: 正常读取
    data = safe_read_csv(test_csv, ["name", "chinese"])
    print(f"测试 1 (正常读取): 获取 {len(data)} 条记录")
    for d in data:
        print(f"  {d['name']}: 语文 {d['chinese']}, 数学 {d['math']}")

    # 测试 2: 缺少列
    data2 = safe_read_csv(test_csv, ["name", "english"])
    print(f"测试 2 (缺少列): 返回 {data2}")

    # 测试 3: 文件不存在
    data3 = safe_read_csv(HERE / "_nonexistent.csv", ["name"])
    print(f"测试 3 (文件不存在): 返回 {data3}")

    # 清理
    test_csv.unlink()
    print("测试全部通过！")

if __name__ == "__main__":
    test_safe_read_csv()
    print("\n异常处理演示完成。")