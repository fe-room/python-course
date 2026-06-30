# 第三阶段：进阶 Python（第 5-6 周）

难度：★★★☆☆ | 前置：完成第二阶段

## 目录

```
03-advanced/
├── README.md
├── week5-advanced/code/
│   ├── day29_generator.py
│   ├── day30_yield_from.py
│   ├── day31_itertools_gen.py
│   ├── day32_closure.py
│   ├── day33_functools.py
│   ├── day34_project_structure/
│   │   ├── pyproject.toml
│   │   └── src/myapp/
│   └── day35_pytest/
│       └── test_todo.py
├── week6-async/code/
│   ├── day36_sync_vs_async.py
│   ├── day37_async_basics.py
│   ├── day38_aiohttp.py
│   ├── day39_async_queue.py
│   ├── day40_async_context.py
│   └── day41_compare_js.md
└── project-async-downloader/
    └── downloader.py
```

## 第 5 周：高级特性

### Day 29 — 生成器

```python
# day29_generator.py
# 生成器 vs 列表：内存对比
import sys

list_comp = [x for x in range(10**6)]       # list：立即占用内存
gen_expr = (x for x in range(10**6))        # generator：惰性求值

print(sys.getsizeof(list_comp))  # ~8MB
print(sys.getsizeof(gen_expr))   # ~104 bytes

# yield
def count_up_to(n):
    i = 0
    while i < n:
        yield i
        i += 1

for num in count_up_to(5):
    print(num)  # 0 1 2 3 4

# 大文件逐行读取
def read_lines(filename):
    with open(filename) as f:
        for line in f:
            yield line.strip()
```

---

### Day 30 — yield from

```python
# day30_yield_from.py
# yield from 委托给另一个生成器
def sub_generator():
    yield "来自子生成器 A"
    yield "来自子生成器 B"

def main_generator():
    yield "来自主生成器"
    yield from sub_generator()  # 委托
    yield "回到主生成器"

for item in main_generator():
    print(item)
# 来自主生成器
# 来自子生成器 A
# 来自子生成器 B
# 回到主生成器

# 实用：逐行读取多个文件
def read_all_lines(*filenames):
    for fname in filenames:
        with open(fname) as f:
            yield from f  # 委托文件迭代器
```

---

### Day 31 — itertools 生成器版

```python
# day31_itertools_gen.py
from itertools import cycle, islice, takewhile, repeat

# cycle：无限循环
def play_songs(songs, max_plays=10):
    for song in islice(cycle(songs), max_plays):
        print(f"播放：{song}")

play_songs(["song1", "song2", "song3"], 7)
# song1, song2, song3, song1, song2, song3, song1

# takewhile：条件满足时取值
nums = [1, 2, 3, 4, 5, 1, 2]
result = list(takewhile(lambda x: x < 4, nums))
print(result)  # [1, 2, 3]
```

---

### Day 32 — 闭包

```python
# day32_closure.py
def make_counter():
    count = 0
    def counter():
        nonlocal count  # 修改外部变量需要 nonlocal
        count += 1
        return count
    return counter

c1 = make_counter()
print(c1())  # 1
print(c1())  # 2
print(c1())  # 3

c2 = make_counter()
print(c2())  # 1（独立的闭包）
```

**对比 JS**：
```javascript
function makeCounter() {
    let count = 0;
    return function() {
        count++;
        return count;
    };
}
```
JS 不需要 `nonlocal`，闭包默认可以修改外部变量

---

### Day 33 — functools

```python
# day33_functools.py
from functools import lru_cache, partial, wraps

# lru_cache：自动缓存
@lru_cache(maxsize=128)
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

# 对比：不加 cache 的 fib(40) 要跑几十秒，加后毫秒级
print(fib(100))  # 354224848179261915075

# partial：固定部分参数
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
cube = partial(power, exp=3)

print(square(5))  # 25
print(cube(5))    # 125
```

---

### Day 34 — 项目结构

```
pyproject.toml:
```toml
[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.10"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.backends._legacy:_Backend"
```

`src/myapp/__init__.py`：空文件
`src/myapp/core.py`：核心逻辑

```
# 安装
pip install -e .     # 开发模式安装，修改代码立即生效
```

---

### Day 35 — pytest

```python
# test_todo.py
# pip install pytest

def test_even_squares():
    from day4_lists import even_squares
    assert even_squares([1, 2, 3, 4]) == [4, 16]
    assert even_squares([]) == []
    assert even_squares([1, 3, 5]) == []

# 运行：pytest test_todo.py -v
```

**进阶用法**：

```python
# conftest.py 共享 fixture
# test_advanced.py — fixture + parametrize

# 运行：pytest test_advanced.py -v
```

详见 `code/day35_pytest/test_advanced.py` 和 `code/day35_pytest/conftest.py`

---

## 第 6 周：异步编程

### Day 36 — 同步 vs 异步

```python
# day36_sync_vs_async.py
import time

# 同步版本
def sync_task(name, delay):
    print(f"开始 {name}")
    time.sleep(delay)
    print(f"完成 {name}")
    return name

def sync_main():
    start = time.time()
    sync_task("A", 2)
    sync_task("B", 2)
    print(f"耗时：{time.time()-start:.1f}s")  # ~4s

sync_main()
```

---

### Day 37 — async/await

```python
# day37_async_basics.py
import asyncio
import time

async def async_task(name, delay):
    print(f"开始 {name}")
    await asyncio.sleep(delay)
    print(f"完成 {name}")
    return name

async def async_main():
    start = time.time()
    # 并发执行
    results = await asyncio.gather(
        async_task("A", 2),
        async_task("B", 2),
    )
    print(f"耗时：{time.time()-start:.1f}s")  # ~2s
    print(results)

asyncio.run(async_main())
```

**对比 JS**：Python 的 `asyncio.gather` = JS 的 `Promise.all`，但 Python 需要 `asyncio.run()` 启动

---

### Day 38 — aiohttp

```python
# day38_aiohttp.py
# pip install aiohttp
import asyncio
import aiohttp

async def fetch_url(session, url):
    async with session.get(url) as resp:
        return await resp.text()

async def main():
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/1",
    ]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        print(f"完成 {len(results)} 个请求")

asyncio.run(main())
```

---

### Day 39 — 异步队列

```python
# day39_async_queue.py
import asyncio
import random

async def worker(name, queue):
    while True:
        url = await queue.get()
        if url is None:
            break
        print(f"[{name}] 处理 {url}")
        await asyncio.sleep(random.random())
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    urls = [f"https://site.com/page/{i}" for i in range(10)]
    for url in urls:
        await queue.put(url)

    # 3 个 worker
    workers = [asyncio.create_task(worker(f"W{i}", queue)) for i in range(3)]
    await queue.join()  # 等待所有任务完成

    # 发送停止信号
    for w in workers:
        await queue.put(None)
    await asyncio.gather(*workers)

asyncio.run(main())
```

---

### Day 40 — 异步上下文管理器

```python
# day40_async_context.py
import asyncio

class AsyncFileReader:
    def __init__(self, filename):
        self.filename = filename

    async def __aenter__(self):
        print(f"打开 {self.filename}")
        self.file = open(self.filename)
        return self

    async def __aexit__(self, *args):
        print(f"关闭 {self.filename}")
        self.file.close()

    async def readline(self):
        await asyncio.sleep(0)  # 模拟异步
        return self.file.readline()

async def main():
    async with AsyncFileReader("test.txt") as reader:
        line = await reader.readline()
        print(line)

asyncio.run(main())
```

### Day 41 — 对比 JS 异步

见 `day41_compare_js.md`

### Day 42 — 周项目：异步下载器

见 `project-async-downloader/downloader.py`

```bash
# 安装依赖
pip install aiohttp

# 运行
python project-async-downloader/downloader.py
```

**项目要求**：
1. 用 `aiohttp` 并发下载多个文件
2. 用 `asyncio.Queue` + 多 worker 控制并发数
3. 显示下载进度和耗时
4. 异常重试（参考 Day 26 retry 装饰器）

**vs JS 对比**：Python 的 `asyncio.gather` = `Promise.all`，`asyncio.Queue` = 自定义并发池