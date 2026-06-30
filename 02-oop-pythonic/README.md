# 第二阶段：面向对象与 Pythonic 编程（第 3-4 周）

难度：★★☆☆☆ | 前置：完成第一阶段

## 目录

```
02-oop-pythonic/
├── README.md
├── week3-oop/code/
│   ├── day15_user.py
│   ├── day16_magic.py
│   ├── day17_property.py
│   ├── day18_inherit.py
│   ├── day19_classmethod.py
│   ├── day20_dataclass.py
│   └── day21_enum.py
├── week4-pythonic/code/
│   ├── day22_collections.py
│   ├── day23_itertools.py
│   ├── day24_contextmanager.py
│   ├── day25_decorator.py
│   ├── day26_retry.py
│   └── day27_typing.py
└── project-todo-class/
    └── todo_manager.py
```

## 第 3 周：面向对象

### Day 15 — class 基础

```python
# day15_user.py
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def greet(self):
        return f"Hi, I'm {self.name}"

# JS 对比
# constructor(name, email) { this.name = name; this.email = email; }
# greet() { return `Hi, I'm ${this.name}`; }

user = User("Alice", "alice@example.com")
print(user.greet())
print(user.name)
```

**关键区别**：
- `__init__` 不是 `constructor`
- `self` 必须显式写（JS 的 `this` 是隐式的）
- 属性直接在 `__init__` 赋值，无需先声明

---

### Day 16 — 魔术方法

```python
# day16_magic.py
from datetime import datetime

class User:
    def __init__(self, name, email):
        self.name, self.email = name, email
        self.created_at = datetime.now()

    def __str__(self):
        return f"User({self.name})"

    def __repr__(self):
        return f"User(name='{self.name}', email='{self.email}')"

    def __eq__(self, other):
        return isinstance(other, User) and self.email == other.email

    def __lt__(self, other):
        return self.name < other.name

u1, u2 = User("Alice", "a@x.com"), User("Bob", "b@x.com")
print(u1)               # User(Alice)
print(u1 == User("A", "a@x.com"))  # True（email 相同）
```

---

### Day 17 — @property

```python
# day17_property.py
from datetime import datetime, timedelta

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self._created_at = datetime.now()

    @property
    def is_new(self):
        return datetime.now() - self._created_at < timedelta(days=7)

    @property
    def email_domain(self):
        return self.email.split("@")[-1]

user = User("Alice", "alice@example.com")
print(user.is_new)        # True
print(user.email_domain)  # example.com
```

**对比 JS**：`@property` = JS 的 `get isNew() { ... }`

---

### Day 18 — 继承

```python
# day18_inherit.py
class AdminUser(User):
    def __init__(self, name, email, permissions=None):
        super().__init__(name, email)
        self.permissions = permissions or ["read"]

    def has_permission(self, perm):
        return perm in self.permissions

    def greet(self):
        return f"Admin {self.name}"

admin = AdminUser("Admin", "admin@x.com", ["read", "write"])
print(admin.is_new)                        # True（继承）
print(admin.has_permission("delete"))      # False
```

---

### Day 19 — @classmethod / @staticmethod

```python
# day19_classmethod.py
import json

class User:
    def __init__(self, name, email):
        self.name, self.email = name, email

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["email"])

    @staticmethod
    def validate_email(email):
        return "@" in email

user = User.from_dict({"name": "Bob", "email": "b@x.com"})
print(User.validate_email("test"))  # True
```

---

### Day 20 — dataclass

```python
# day20_dataclass.py
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Todo:
    title: str
    done: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    tags: list = field(default_factory=list)

todo = Todo(title="学习 dataclass")
print(todo)  # Todo(title='学习 dataclass', done=False, ...)
todo.done = True
```

**自动生成**：`__init__`、`__repr__`、`__eq__` — 少写很多样板代码

---

### Day 21 — Enum + __post_init__

```python
# day21_enum.py
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime

class Status(Enum):
    PENDING = auto()
    DONE = auto()
    ARCHIVED = auto()

@dataclass
class Todo:
    title: str
    status: Status = Status.PENDING
    tags: list = None
    created_at: datetime = None

    def __post_init__(self):
        """__init__ 后自动调用，适合做校验和默认值"""
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()

    def complete(self):
        self.status = Status.DONE

todo = Todo("学习 Enum")
print(todo.status.name)     # PENDING
todo.complete()
print(todo.status.name)     # DONE
```

---

## 第 4 周：Pythonic 编程

### Day 22 — collections

```python
# day22_collections.py
from collections import defaultdict, Counter, deque

# defaultdict：不存在 key 时自动创建
freq = defaultdict(int)
for w in ["a", "b", "a", "c"]:
    freq[w] += 1
print(dict(freq))            # {'a': 2, 'b': 1, 'c': 1}

# Counter：计数 + 排序
cnt = Counter("hello world".split())
print(cnt.most_common(1))    # [('hello', 1)]

# deque：双端队列
q = deque([1, 2, 3])
q.appendleft(0)
print(q.popleft())           # 0
```

---

### Day 23 — itertools

```python
# day23_itertools.py
from itertools import chain, product, cycle, islice

# chain：合并
print(list(chain([1,2], [3,4])))  # [1,2,3,4]

# product：笛卡尔积
print(list(product([1,2], "ab")))  # [(1,'a'),(1,'b'),(2,'a'),(2,'b')]

# cycle：无限循环
for item in islice(cycle("ABC"), 5):
    print(item, end=" ")  # A B C A B
```

---

### Day 24 — 上下文管理器

```python
# day24_contextmanager.py
import time
from contextlib import contextmanager

# 方式 1: class
class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self
    def __exit__(self, *args):
        print(f"耗时：{(time.perf_counter()-self.start)*1000:.1f}ms")

# 方式 2: 装饰器（更简洁）
@contextmanager
def timer():
    start = time.perf_counter()
    yield
    print(f"耗时：{(time.perf_counter()-start)*1000:.1f}ms")

with timer():
    sum(range(10**6))
```

---

### Day 25 — 装饰器

```python
# day25_decorator.py
from functools import wraps

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] 调用 {func.__name__}({args}, {kwargs})")
        return func(*args, **kwargs)
    return wrapper

@log_call
def add(a, b):
    return a + b

print(add(3, 4))
# [LOG] 调用 add((3, 4), {})
# 7
```

---

### Day 26 — 带参数装饰器

```python
# day26_retry.py
from functools import wraps
import random

def retry(max_attempts=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == max_attempts - 1:
                        raise
                    print(f"重试 {i+1}/{max_attempts}")
        return wrapper
    return decorator

@retry(max_attempts=3)
def unstable():
    if random.random() < 0.7:
        raise ConnectionError("网络错误")
    return "成功"

print(unstable())
```

---

### Day 27 — 类型注解

```python
# day27_typing.py
from typing import Optional, Union, List, Dict, Tuple

# 基础
name: str = "Alice"
age: int = 25

# 容器
items: List[int] = [1, 2, 3]
scores: Dict[str, int] = {"math": 90}
maybe: Optional[str] = None   # str | None

# 函数
def process(data: List[int]) -> Dict[str, float]:
    return {"sum": sum(data), "avg": sum(data)/len(data)}

# 运行 mypy 检查
# pip install mypy && mypy day27_typing.py
```

---

### Day 28 — 周项目：Todo Class 重构

回顾 `project-todo-class/todo_manager.py`，确保理解：
- `@dataclass` + `Enum` 替代手写 class
- `__post_init__` 做字段校验
- `@property` 替代 getter 方法
- JSON 序列化/反序列化（`asdict` + `isoformat`）

**挑战任务**：
1. 添加 `@timer` 装饰器测量每个操作耗时
2. 用 `contextlib.contextmanager` 实现自动保存的上下文
3. 为项目添加 `requirements.txt`
```