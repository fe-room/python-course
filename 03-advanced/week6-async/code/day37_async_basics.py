"""
Day 37 — async/await 基础 + asyncio.gather
============================================
对于前端工程师：
  Python  async def  ≈  JS  async function
  Python  await       ≈  JS  await
  Python  asyncio.gather()  ≈  JS  Promise.all()

关键区别：
  - JS 中 await 只能在 async function 内部使用
  - Python 中 await 只能在 async def 内部使用
  - JS 的 Promise 会自动「热启动」
  - Python 的 coroutine 需要事件循环驱动 (asyncio.run / loop.run_until_complete)
"""

import asyncio
import datetime


# ── 定义异步任务 ──
# JS 版:
#   async function task(name) {
#     console.log(`[start] ${name}`);
#     await new Promise(r => setTimeout(r, 2000));
#     console.log(`[end] ${name}`);
#     return `${name} result`;
#   }

async def task(name: str) -> str:
    """异步任务：await asyncio.sleep 不阻塞线程"""
    print(f"  [开始] {name}  @ {datetime.datetime.now().strftime('%H:%M:%S')}")
    await asyncio.sleep(2)           # 异步 sleep → 让出控制权
    print(f"  [结束] {name}  @ {datetime.datetime.now().strftime('%H:%M:%S')}")
    return f"{name} 结果"


async def main():
    print("=" * 50)
    print("异步版本：两个任务并发执行，总耗时 ≈ 2 秒")
    print("=" * 50)
    print()

    t0 = asyncio.get_event_loop().time()

    # ── 方式 1：顺序 await（仍然是串行，不推荐）──
    #   r1 = await task("任务A")
    #   r2 = await task("任务B")   ← 等 r1 完成才开始

    # ── 方式 2：并发执行（推荐）──
    # JS 版:
    #   const [r1, r2] = await Promise.all([
    #     task("任务A"),
    #     task("任务B"),
    #   ]);
    r1, r2 = await asyncio.gather(
        task("任务A"),
        task("任务B"),
    )

    elapsed = asyncio.get_event_loop().time() - t0

    print()
    print(f"结果: r1 = {r1}")
    print(f"结果: r2 = {r2}")
    print(f"总耗时: {elapsed:.2f} 秒  ← 两个任务并行，约 2 秒")
    print()
    print("🎉 耗时减半！sleep 期间事件循环去执行其他任务了")

    # ── 高级用法：gather 返回顺序与任务顺序一致 ──
    print()
    print("--- gather 特性 ---")
    print("gather() 返回值顺序 = 传入任务顺序，与完成顺序无关")
    print("如果任一任务抛异常，gather 会抛异常（除非 return_exceptions=True）")


if __name__ == "__main__":
    # Python 3.7+ 推荐方式
    asyncio.run(main())
