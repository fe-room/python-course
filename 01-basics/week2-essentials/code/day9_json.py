"""
day9_json.py — JSON 序列化与配置文件校验
=========================================
知识点：
  1. json.dumps / json.loads — 内存中的序列化
  2. json.dump / json.load — 文件读写
  3. indent / ensure_ascii 参数
  4. 实战：配置文件字段校验
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# 1. json.dumps — Python 对象 → JSON 字符串
# ---------------------------------------------------------------------------
print("=" * 50)
print("1. json.dumps — 序列化 Python 对象为字符串")
print("=" * 50)

data = {
    "name": "Python 课程",
    "version": 1.0,
    "students": ["Alice", "Bob", "Charlie"],
    "active": True,
    "config": {"max_retries": 3, "timeout": 30},
}

# 默认输出：一行紧凑格式
compact = json.dumps(data)
print("紧凑格式:")
print(compact)

# 带缩进：更易读
pretty = json.dumps(data, indent=2, ensure_ascii=False)
print("\n带缩进 (indent=2, ensure_ascii=False):")
print(pretty)

# ensure_ascii=True (默认): 非 ASCII 字符会被转义为 \uXXXX
ascii_escaped = json.dumps({"msg": "你好"}, ensure_ascii=True)
print("\nensure_ascii=True:")
print(ascii_escaped)  # {"msg": "\u4f60\u597d"}

# ensure_ascii=False: 保留原始字符
no_ascii = json.dumps({"msg": "你好"}, ensure_ascii=False)
print("\nensure_ascii=False:")
print(no_ascii)  # {"msg": "你好"}

# ---------------------------------------------------------------------------
# 2. json.loads — JSON 字符串 → Python 对象
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("2. json.loads — 反序列化字符串为 Python 对象")
print("=" * 50)

json_str = '{"name": "Alice", "scores": [90, 85, 88]}'
parsed = json.loads(json_str)
print(f"解析结果: {parsed}")
print(f"name: {parsed['name']}")
print(f"scores 类型: {type(parsed['scores'])}")

# ---------------------------------------------------------------------------
# 3. json.dump / json.load — 直接读写文件
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("3. json.dump / json.load — 文件读写")
print("=" * 50)

demo_json = HERE / "demo_config.json"

# 写入 JSON 文件
config = {
    "app_name": "MyApp",
    "debug": True,
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "mydb",
    },
}
with open(demo_json, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"已写入 {demo_json.name}")

# 读取 JSON 文件
with open(demo_json, "r", encoding="utf-8") as f:
    loaded = json.load(f)

print(f"读取结果: {loaded}")
print(f"database host: {loaded['database']['host']}")

# 清理
demo_json.unlink()

# ---------------------------------------------------------------------------
# 4. 练习题：配置文件校验
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("练习题：配置文件校验 (validate_config)")
print("=" * 50)
"""
请实现函数 validate_config(config, required_fields)：
  - config: 字典，待校验的配置
  - required_fields: 列表，必须存在的字段名（支持嵌套，如 "database.host"）
  - 如果缺少字段，抛出 ValueError，提示缺少了哪些字段
  - 所有字段都存在则返回 True
"""

# ---------- 你的代码从这里开始 ----------

def validate_config(config, required_fields):
    """
    校验配置中是否包含所有必需的字段。
    支持嵌套字段，用点号分隔，例如 "database.host"。
    """
    missing = []
    for field in required_fields:
        parts = field.split(".")
        current = config
        # 沿着路径逐层查找
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                missing.append(field)
                break
    if missing:
        raise ValueError(f"缺少必需字段: {', '.join(missing)}")
    return True

# ---------- 测试 ----------

def test_validate_config():
    config = {
        "app_name": "MyApp",
        "version": "1.0",
        "database": {
            "host": "localhost",
            "port": 5432,
        },
        "features": {
            "logging": True,
        },
    }

    # 测试 1: 全部存在 → True
    result = validate_config(config, ["app_name", "database.host"])
    print(f"测试 1 (全部存在): {result}")

    # 测试 2: 缺少字段 → ValueError
    try:
        validate_config(config, ["app_name", "database.password", "features.nonexistent"])
    except ValueError as e:
        print(f"测试 2 (缺少字段): {e}")

    # 测试 3: 顶层字段缺少
    try:
        validate_config(config, ["api_key"])
    except ValueError as e:
        print(f"测试 3 (缺少顶层字段): {e}")

    print("测试全部通过！")

if __name__ == "__main__":
    test_validate_config()
    print("\nJSON 操作演示完成。")