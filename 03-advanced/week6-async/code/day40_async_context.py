"""
Day 40 — 异步上下文管理器：__aenter__ / __aexit__
=================================================
对于前端工程师：
  Python  async with  ≈  JS 无直接等价物
  JS 有 Symbol.asyncDispose (ES2024+ 的 using 声明)
  但主流 JS 代码仍习惯 try/finally

场景：异步文件读取、数据库连接、aiohttp session 等
"""

import asyncio
import aiofiles   # pip install aiofiles


# ── 自定义异步上下文管理器 ──
class AsyncFileReader:
    """
    模拟异步文件读取器

    如果不想手动实现 __aenter__ / __aexit__，
    也可以用 @asynccontextmanager 装饰器（类似 JS generator）
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.file = None

    async def __aenter__(self):
        """进入 async with 块时调用（类似 JS 中 await setup()）"""
        print(f"  [__aenter__] 打开文件: {self.filename}")
        # 模拟异步打开文件操作
        await asyncio.sleep(0.2)
        self.file = f"FILE_HANDLE:{self.filename}"
        print(f"  [__aenter__] 文件已打开: {self.file}")
        return self  # 返回绑定到 'as' 子句的对象

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """离开 async with 块时调用（类似 finally）"""
        print(f"  [__aexit__] 关闭文件: {self.filename}")
        await asyncio.sleep(0.1)  # 模拟异步关闭
        self.file = None
        print(f"  [__aexit__] 文件已关闭")

        # 返回 False 表示不抑制异常，True 则抑制
        # 类似 JS try/catch 中是否 rethrow
        if exc_type is not None:
            print(f"  [__aexit__] 捕获到异常: {exc_type.__name__}: {exc_val}")
            # return True   ← 抑制异常，不向外传播
        return False  # 不抑制，异常继续向外传播

    async def read(self) -> str:
        """模拟异步读取文件内容"""
        if self.file is None:
            raise RuntimeError("文件未打开，请使用 async with 管理")
        await asyncio.sleep(0.3)
        return f"这是 {self.filename} 的模拟内容（行1\\n行2\\n行3）"


# ── 方式 2：使用 @asynccontextmanager 装饰器（更简洁） ──
from contextlib import asynccontextmanager


@asynccontextmanager
async def async_db_connection(db_name: str):
    """
    使用装饰器的版本（类似于 JS 中 async generator 配合 for await...of）

    JS 无直接等价物，但可用 async generator 模拟：
      async function* dbConnection(name) {
        console.log('connect');
        yield { query: async (sql) => ... };
        console.log('disconnect');
      }
    """
    print(f"  [connect] 连接数据库: {db_name}")
    await asyncio.sleep(0.2)

    # yield 之前的代码 = __aenter__
    # yield 的值 = 'as' 绑定的对象
    class _Connection:
        async def query(self, sql: str) -> str:
            await asyncio.sleep(0.1)
            return f"[{db_name}] 查询结果: {sql}"

    try:
        yield _Connection()
    finally:
        # finally 中的代码 = __aexit__
        print(f"  [disconnect] 断开数据库: {db_name}")
        await asyncio.sleep(0.1)


async def main():
    print("=" * 60)
    print("异步上下文管理器 (async context manager)")
    print("=" * 60)
    print()

    # ── 方式 1：自定义 __aenter__ / __aexit__ ──
    print("--- 1. 自定义 AsyncFileReader ---")
    async with AsyncFileReader("data.txt") as reader:
        content = await reader.read()
        print(f"  读取内容: {content}")
    print("  (已自动关闭，无需手动 close)")
    print()

    # ── 方式 2：@asynccontextmanager 装饰器 ──
    print("--- 2. @asynccontextmanager 装饰器 ---")
    async with async_db_connection("mydb") as conn:
        result = await conn.query("SELECT * FROM users")
        print(f"  {result}")
    print("  (已自动断开连接)")
    print()

    # ── 异常处理演示 ──
    print("--- 3. 异常处理 ---")
    try:
        async with AsyncFileReader("secret.txt") as reader:
            print(f"  file 状态: {reader.file}")
            raise ValueError("模拟读取错误")
    except ValueError as e:
        print(f"  外部捕获到异常: {e}")
    print()

    # ── 多个上下文管理器（类似 JS 嵌套 await） ──
    print("--- 4. 多个 async with（可组合） ---")
    async with AsyncFileReader("a.txt") as f1, \
               AsyncFileReader("b.txt") as f2:
        c1 = await f1.read()
        c2 = await f2.read()
        print(f"  f1: {c1}")
        print(f"  f2: {c2}")


if __name__ == "__main__":
    asyncio.run(main())
