# 第一阶段：Python 基础（第 1-2 周）

难度：★☆☆☆☆ | 目标：掌握 Python 基础语法，能写脚本

## 目录

```
01-basics/
├── README.md              ← 本文件
├── week1-syntax/          # 第 1 周：语法速通
│   └── code/
│       ├── day1_hello.py
│       ├── day2_bmi.py
│       ├── day3_strings.py
│       ├── day4_lists.py
│       ├── day5_dicts.py
│       ├── day6_control.py
│       └── day7_functions.py
├── week2-essentials/      # 第 2 周：基础巩固
│   └── code/
│       ├── day8_files.py
│       ├── day9_json.py
│       ├── day10_errors.py
│       ├── day11_modules/
│       │   ├── __init__.py
│       │   ├── calc.py
│       │   └── strings.py
│       ├── day12_comprehensions.py
│       └── day13_stdlib.py
└── project-cli-todo/      # 第 2 周末项目
    └── todo.py
```

## 第 1 周：语法速通

### Day 1 — 环境搭建

目标：装好 Python 环境，跑通第一个程序

```bash
# macOS
brew install pyenv
pyenv install 3.12.0
pyenv global 3.12.0

# 验证
python3 --version  # Python 3.12.0

# 虚拟环境
mkdir python-course && cd python-course
python3 -m venv .venv
source .venv/bin/activate
```

```python
# day1_hello.py
print("Hello, Python!")
name = input("你的名字：")
print(f"你好，{name}！")
```

运行：`python3 day1_hello.py`

**关键概念**：`print()`、`input()`、f-string、`.venv`、`pip`

---

### Day 2 — 变量与类型

```python
# day2_bmi.py
height = float(input("身高(m)："))
weight = float(input("体重(kg)："))
bmi = weight / (height ** 2)

if bmi < 18.5:
    level = "偏瘦"
elif bmi < 24:
    level = "正常"
elif bmi < 28:
    level = "偏胖"
else:
    level = "肥胖"

print(f"BMI = {bmi:.1f}，{level}")
```

**关键概念**：`int/float/str/bool/None`、`type()`、类型转换
**对比 JS**：`5 / 2` → `2.5`（永远是 float），`//` 是整除，没有 `===`

---

### Day 3 — 字符串

```python
# day3_strings.py
# 切片
s = "Python"
print(s[0])     # P
print(s[-1])    # n
print(s[0:3])   # Pyt（左闭右开）
print(s[::-1])  # nohtyP

# 方法
print("hello world".split())       # ['hello', 'world']
print("  abc  ".strip())            # abc
print("hello".replace("l", "x"))   # hexxo

# f-string
name, age = "Bob", 30
print(f"{name} is {age} years old")
print(f"{3.14159:.2f}")  # 3.14

# 练习：日志格式化
from datetime import datetime
def format_log(level, message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{now}] [{level.upper()}] {message}"

print(format_log("info", "服务启动"))
```

---

### Day 4 — 列表

```python
# day4_lists.py
fruits = ["apple", "banana", "cherry"]
fruits.append("date")
fruits.insert(0, "avocado")
fruits.remove("banana")
popped = fruits.pop()

# 切片
nums = [0, 1, 2, 3, 4, 5]
print(nums[1:4])    # [1, 2, 3]
print(nums[::-1])   # [5, 4, 3, 2, 1, 0]

# 列表推导式
print([x * 2 for x in range(5)])  # [0, 2, 4, 6, 8]
print([x for x in range(10) if x % 2 == 0])  # [0, 2, 4, 6, 8]

# 遍历
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# 练习：偶数平方
def even_squares(numbers):
    return [n * n for n in numbers if n % 2 == 0]

print(even_squares([1, 2, 3, 4, 5, 6]))  # [4, 16, 36]
```

**对比 JS**：Python list = JS array，但没有 `map/filter`（用推导式替代）

---

### Day 5 — 字典

```python
# day5_dicts.py
user = {"name": "Alice", "age": 25}
print(user.get("name"))          # Alice
print(user.get("email", "N/A"))  # N/A（带默认值）
user["email"] = "alice@example.com"

# 遍历
for key, val in user.items():
    print(f"{key}: {val}")

# 字典推导式
print({x: x**2 for x in range(5)})  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 练习：单词频率
text = "hello world hello python hello world"
freq = {}
for word in text.split():
    freq[word] = freq.get(word, 0) + 1
top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:3]
print(top)
```

**对比 JS**：Python dict = JS Object + Map 的结合体。`.get(key, default)` 是 Python 特色。

---

### Day 6 — 控制流

```python
# day6_control.py
# if/elif/else
score = 85
grade = "A" if score >= 90 else "B" if score >= 80 else "C"
print(grade)  # B

# for + range
for i in range(5):        # 0,1,2,3,4
    print(i, end=" ")

# enumerate
for i, val in enumerate(["a", "b", "c"]):
    print(f"{i}: {val}")

# 练习：99 乘法表
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f"{j}x{i}={i*j}", end="\t")
    print()

# 练习：FizzBuzz
for i in range(1, 101):
    if i % 15 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
```

---

### Day 7 — 函数

```python
# day7_functions.py
def greet(name):
    return f"Hello, {name}"

def power(base, exp=2):
    return base ** exp

def sum_all(*numbers):
    return sum(numbers)

def create_user(**kwargs):
    return kwargs

print(sum_all(1, 2, 3, 4))  # 10
print(create_user(name="Alice", age=25))

# 类型注解
def add(a: int, b: int) -> int:
    return a + b

# 练习：计算器
def calc(operator, *numbers):
    if operator == "add":
        return sum(numbers)
    elif operator == "mul":
        r = 1
        for n in numbers:
            r *= n
        return r

print(calc("add", 1, 2, 3))   # 6
print(calc("mul", 2, 3, 4))   # 24
```

---

## 第 2 周：基础巩固

### Day 8 — 文件操作

```python
# day8_files.py
# 写文件
with open("test.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n第二行\n")

# 读文件
with open("test.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())

# pathlib（推荐）
from pathlib import Path
path = Path("data") / "notes.txt"
path.parent.mkdir(exist_ok=True)
path.write_text("hello")
print(path.read_text())  # hello

# 练习：CSV 解析
with open("sample.csv", "w") as f:
    f.write("name,score\nAlice,85\nBob,92\n")

scores = []
with open("sample.csv") as f:
    next(f)  # 跳过标题
    for line in f:
        scores.append(int(line.strip().split(",")[1]))
print(f"平均分：{sum(scores)/len(scores):.1f}")
```

---

### Day 9 — JSON

```python
# day9_json.py
import json

data = {"name": "Alice", "age": 25}
# 序列化
print(json.dumps(data, indent=2, ensure_ascii=False))
# 反序列化
parsed = json.loads('{"name": "Bob"}')
print(parsed["name"])

# 文件读写
with open("config.json", "w") as f:
    json.dump(data, f, indent=2)
with open("config.json") as f:
    loaded = json.load(f)

# 练习：配置校验
config = json.loads('{"host": "localhost", "port": 8080}')
required = ["host", "port", "database"]
for field in required:
    if field not in config:
        print(f"缺少: {field}")
```

---

### Day 10 — 异常处理

```python
# day10_errors.py
try:
    num = int(input("输入数字："))
    result = 10 / num
except ValueError:
    print("请输入有效数字")
except ZeroDivisionError:
    print("不能除以零")
except Exception as e:
    print(f"未知错误：{e}")
else:
    print(f"结果是：{result}")
finally:
    print("结束")

# 自定义异常
class ValidationError(Exception):
    pass

def validate_age(age):
    if age < 0:
        raise ValidationError("年龄不能为负数")

# 练习：安全 CSV 解析
def safe_read(filename):
    try:
        with open(filename) as f:
            return f.readlines()
    except FileNotFoundError:
        return []
```

---

### Day 11 — 模块与包

```
code/day11_modules/
├── __init__.py
├── calc.py          # add(), multiply()
└── strings.py       # reverse(), count_words()
```

```python
# day11_modules/calc.py
def add(a, b): return a + b
def multiply(a, b): return a * b
```

```python
# day11_modules/strings.py
def reverse(s): return s[::-1]
def count_words(s): return len(s.split())
```

```python
# 导入使用
from day11_modules.calc import add, multiply
from day11_modules.strings import reverse

print(add(3, 4))       # 7
print(reverse("hello"))  # olleh

# __name__ 守卫
if __name__ == "__main__":
    print("这是主程序")
```

---

### Day 12 — 列表推导式进阶

```python
# day12_comprehensions.py
# 带条件
[x for x in range(20) if x % 2 == 0]

# 嵌套循环
[x*y for x in range(1,4) for y in range(1,4)]

# 三元
["even" if x % 2 == 0 else "odd" for x in range(5)]

# dict/set 推导式
{w: len(w) for w in ["hello", "world"]}
{x % 3 for x in range(10)}

# 一行练习：过滤奇数并平方
result = [x*x for x in range(20) if x % 2 == 1]
```

---

### Day 13 — 标准库入门

```python
# day13_stdlib.py
from datetime import datetime, timedelta
import random, math

now = datetime.now()
print(now.strftime("%Y-%m-%d %H:%M"))

yesterday = now - timedelta(days=1)
print(yesterday.strftime("%A"))

print(random.randint(1, 100))
print(math.sqrt(16))     # 4.0
print(math.floor(3.7))   # 3

# 练习：每日一句
quotes = ["Keep it simple", "代码是写给人读的"]
print(f"[{now:%H:%M}] {random.choice(quotes)}")
```

---

### Day 14 — 项目复盘 + 依赖管理

```python
# 生成 requirements.txt
# 终端运行：pip freeze > requirements.txt
# 安装依赖：pip install -r requirements.txt

# day1_venv.py（新建）
# 演示 requirements.txt 格式
requirements_example = """
# 生产依赖
fastapi==0.110.0
uvicorn==0.27.0

# 开发依赖（保存在 requirements-dev.txt）
pytest==8.0.0
"""
print("pip freeze > requirements.txt  # 导出当前环境依赖")
print("pip install -r requirements.txt  # 安装依赖")
```

**关键概念**：`pip freeze`、`requirements.txt`、虚拟环境隔离
**周末项目**：完善 CLI Todo 项目，添加分类和搜索功能（基于已有的 todo.py）

---

## 第 2 周末项目：CLI Todo List

文件：`project-cli-todo/todo.py`

要求：
1. 文件持久化（JSON）
2. 增删改查
3. 标记完成/未完成
4. 命令行交互

详见 `project-cli-todo/todo.py`