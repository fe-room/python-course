# Day 41 — Python Async vs JavaScript Async 对比

> 面向前端工程师，从 JS 异步知识迁移到 Python 异步。

---

## 一、核心概念对照表

| 概念 | JavaScript | Python |
|------|-----------|--------|
| 定义异步函数 | `async function foo() {}` | `async def foo():` |
| 等待结果 | `await promise` | `await coroutine` |
| 启动事件循环 | 浏览器 / Node.js 自动管理 | `asyncio.run(main())` |
| 并发执行 | `Promise.all([p1, p2])` | `asyncio.gather(t1, t2)` |
| 等待首个完成 | `Promise.race([p1, p2])` | `asyncio.wait([t1, t2], return_when=FIRST_COMPLETED)` |
| 超时控制 | `Promise.race([task, timeoutPromise])` | `asyncio.wait_for(task, timeout=5)` |
| 延迟 / sleep | `new Promise(r => setTimeout(r, 1000))` | `await asyncio.sleep(1)` |
| HTTP 请求 | `fetch(url)` | `aiohttp.ClientSession().get(url)` |
| 任务队列 | 无内置（手动事件 + 数组） | `asyncio.Queue` |
| 上下文管理 | `using` (ES2024+) / try-finally | `async with` (`__aenter__` / `__aexit__`) |
| 异常处理 | `try/catch` | `try/except` (在 async def 内) |
| 事件循环类型 | 单线程事件循环 | 单线程事件循环（但可用多进程扩展） |

---

## 二、关键差异详解

### 1. 事件循环的启动方式

**JavaScript** — 浏览器 / Node.js 自动启动事件循环，`async` 函数开箱即用：

```js
// JS — 无需手动启动事件循环
async function main() {
  const data = await fetch('/api/data');
  console.log(data);
}
main(); // 浏览器自动调度
```

**Python** — 需要显式调用 `asyncio.run()` 启动事件循环：

```python
# Python — 必须显式启动事件循环
async def main():
    data = await fetch_data()
    print(data)

asyncio.run(main())  # 创建并运行事件循环
```

> 这是最大的认知差异：Python 的事件循环需要你「手动点火」。

### 2. `await` 的细微差别

| 特性 | JS | Python |
|------|----|--------|
| await 非 Promise 值 | 自动包装为 `Promise.resolve(val)` | 不会包装，直接返回 |
| await 一个 coroutine | ❌ 语法错误 | ✅ 会执行 coroutine |
| 忘记 await | Promise 对象悬浮（不会报错） | `RuntimeWarning: coroutine was never awaited` |

```python
# Python 中忘记 await 会得到警告
async def foo():
    return 42

result = foo()       # ⚠️ 不会执行！得到一个 coroutine 对象
print(result)        # <coroutine object foo at 0x...>
result = await foo() # ✅ 正确
```

### 3. Promise 自动执行 vs Coroutine 惰性执行

**JavaScript** 中 Promise 一旦创建就立即开始执行：

```js
// Promise 是「热」的 — 创建即执行
const p = new Promise(resolve => {
  console.log('Promise 开始执行'); // 立即输出
  resolve(42);
});
// 不需要 await，Promise 已经在跑了
```

**Python** 中 Coroutine 是「冷」的 — 只有 await 才会执行：

```python
# Coroutine 是「冷」的 — 不 await 就不会执行
async def foo():
    print('这行永远不会输出')

c = foo()          # 只是创建了 coroutine 对象，没执行
# await c          # 只有 await 才会真正执行
```

> 这意味着在 Python 中，`asyncio.gather(t1(), t2())` 中的 `t1()` 和 `t2()` 调用只是创建 coroutine，`gather` 负责调度它们。而在 JS 中，`Promise.all([p1, p2])` 传入的 Promise 可能已经在执行了。

### 4. 并发执行对比

| 场景 | JavaScript | Python |
|------|-----------|--------|
| 全部完成 | `Promise.all()` | `asyncio.gather()` |
| 任意完成 | `Promise.race()` | `asyncio.wait(return_when=FIRST_COMPLETED)` |
| 全部完成（容错） | `Promise.allSettled()` | `asyncio.gather(return_exceptions=True)` |
| 按序迭代 | `for...of` + await | `async for` (异步迭代器) |

### 5. HTTP 请求对比

```python
# Python aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
        data = await resp.json()
```

```js
// JS fetch
const resp = await fetch(url);
const data = await resp.json();
```

> aiohttp 的 `ClientSession` 提供了连接池复用，性能更好。JS 的 `fetch` 更简洁。

### 6. 异步迭代器

```python
# Python — async for
async for chunk in async_stream():
    process(chunk)
```

```js
// JS — for await...of
for await (const chunk of asyncStream) {
  process(chunk);
}
```

> 两者语法几乎相同，但 Python 基于 `__aiter__` / `__anext__` 协议，JS 基于 `Symbol.asyncIterator`。

---

## 三、等价的代码片段

### 延时执行

```js
// JS
await new Promise(r => setTimeout(r, 2000));
```

```python
# Python
await asyncio.sleep(2)
```

### 并发请求

```js
// JS
const [user, posts] = await Promise.all([
  fetch('/api/user').then(r => r.json()),
  fetch('/api/posts').then(r => r.json()),
]);
```

```python
# Python
async with aiohttp.ClientSession() as s:
    user_task = s.get('/api/user')
    posts_task = s.get('/api/posts')
    user_resp, posts_resp = await asyncio.gather(user_task, posts_task)
    user = await user_resp.json()
    posts = await posts_resp.json()
```

### 超时控制

```js
// JS
const result = await Promise.race([
  fetch('/api/slow'),
  new Promise((_, reject) =>
    setTimeout(() => reject(new Error('超时')), 5000)
  ),
]);
```

```python
# Python
try:
    result = await asyncio.wait_for(
        session.get('/api/slow'),
        timeout=5
    )
except asyncio.TimeoutError:
    print('超时')
```

---

## 四、总结

| 维度 | JavaScript | Python |
|------|-----------|--------|
| 学习曲线 | 较平缓（浏览器自动管理事件循环） | 略陡（需理解事件循环 + await 规则） |
| 生态成熟度 | 非常高（Node.js 天生异步） | 较高（aiohttp / asyncpg / aiofiles） |
| 写法简洁度 | 更简洁（`fetch` 内置） | 稍繁琐（需额外库） |
| 并发控制 | Promise API 丰富 | asyncio 工具完整 |
| 适合场景 | IO 密集型（Web 服务） | IO 密集型（爬虫 / API / 数据管道） |
| 多核利用 | Worker Threads | `asyncio.to_thread` / `concurrent.futures` |

> **一句话总结**：Python 的 async/await 借鉴了 JS/C# 的设计，核心概念相同，但 Python 要求更显式地管理事件循环，且 coroutine 是惰性的（不会自动执行）。
