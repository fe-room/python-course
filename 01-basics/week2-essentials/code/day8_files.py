"""
day8_files.py — 文件读写与 pathlib 入门
=========================================
知识点：
  1. 用 with open() 读写文本文件
  2. 用 pathlib.Path 优雅地操作路径
  3. 简单的 CSV 读写
"""

from pathlib import Path  # 面向对象的文件路径库
import csv
import sys

# ---------------------------------------------------------------------------
# 1. 基本的文件写入与读取
# ---------------------------------------------------------------------------

# 获取当前文件所在目录，保证路径不出错
HERE = Path(__file__).parent
demo_file = HERE / "demo_output.txt"  # 使用 / 拼接路径，比 os.path.join 更直观

print("=" * 50)
print("1. 基本的文件写入与读取")
print("=" * 50)

# --- 写入 ---
# with 语句会自动关闭文件，即使发生异常也会关闭
lines = ["第一行", "第二行", "第三行"]
with open(demo_file, "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")

print(f"已写入 {len(lines)} 行到 {demo_file.name}")

# --- 读取全部内容 ---
with open(demo_file, "r", encoding="utf-8") as f:
    content = f.read()
print(f"\n读取全部内容:\n{content}")

# --- 按行读取 ---
with open(demo_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        print(f"第{i}行: {line.strip()}")

# 清理临时文件
demo_file.unlink()  # 删除文件

# ---------------------------------------------------------------------------
# 2. pathlib 常用操作
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("2. pathlib 常用操作")
print("=" * 50)

p = Path("/usr/local/bin/python3")
print(f"路径:          {p}")
print(f"父目录:        {p.parent}")          # /usr/local/bin
print(f"文件名:        {p.name}")            # python3
print(f"不带后缀名:    {p.stem}")            # python
print(f"后缀:          {p.suffix}")          # .3 (嗯，不太标准)
print(f"是否存在:      {p.exists()}")
print(f"是文件吗:      {p.is_file()}")
print(f"是目录吗:      {p.is_dir()}")

# 遍历当前目录下的所有 .py 文件
print("\n当前目录下所有 .py 文件:")
for py_file in HERE.glob("*.py"):
    print(f"  - {py_file.name}")

# ---------------------------------------------------------------------------
# 3. CSV 读写示例
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("3. CSV 读写示例")
print("=" * 50)

csv_file = HERE / "demo_scores.csv"

# 写入 CSV
headers = ["name", "score", "passed"]
rows = [
    ["Alice", 88, "Yes"],
    ["Bob", 55, "No"],
    ["Charlie", 72, "Yes"],
]

with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"已写入 {len(rows)} 条记录到 {csv_file.name}")

# 读取 CSV
with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)  # 跳过表头
    print(f"表头: {header}")
    for row in reader:
        name, score, passed = row
        print(f"  {name}: {score} 分, {'通过' if passed == 'Yes' else '未通过'}")

# 用 DictReader 更直观
print("\n使用 DictReader 读取:")
with open(csv_file, "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(f"  {row['name']}: {row['score']} 分")

# 清理
csv_file.unlink()

# ---------------------------------------------------------------------------
# 练习题：解析成绩 CSV
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("练习题：解析成绩 CSV")
print("=" * 50)
"""
请在下方实现函数 parse_grades(csv_path)，它接收一个 CSV 文件路径，
CSV 内容为：
  name,chinese,math,english
  Alice,90,85,88
  Bob,70,60,55
  Charlie,80,95,92

函数应返回一个列表，每个元素是字典：
  {"name": "Alice", "total": 263, "average": 87.67}

并且只保留平均分 >= 80 的学生。
"""
# ---------- 你的代码从这里开始 ----------

def parse_grades(csv_path):
    """解析成绩 CSV，返回平均分 >= 80 的学生列表"""
    result = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            chinese = int(row["chinese"])
            math = int(row["math"])
            english = int(row["english"])
            total = chinese + math + english
            average = round(total / 3, 2)
            if average >= 80:
                result.append({
                    "name": row["name"],
                    "total": total,
                    "average": average,
                })
    return result

# ---------- 测试 ----------

def test_parse_grades():
    test_csv = HERE / "_test_grades.csv"
    with open(test_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "chinese", "math", "english"])
        writer.writerow(["Alice", 90, 85, 88])
        writer.writerow(["Bob", 70, 60, 55])
        writer.writerow(["Charlie", 80, 95, 92])

    grades = parse_grades(test_csv)
    test_csv.unlink()  # 用完删除

    print("解析结果:")
    for g in grades:
        print(f"  {g['name']}: 总分 {g['total']}, 平均 {g['average']}")

    # 简单断言验证
    assert len(grades) == 2, "应该只有 2 个学生达标"
    assert grades[0]["name"] == "Alice"
    assert grades[1]["name"] == "Charlie"
    print("所有断言通过！")

if __name__ == "__main__":
    print("\n--- 运行测试 ---")
    test_parse_grades()
    print("\n文件操作演示完成。")