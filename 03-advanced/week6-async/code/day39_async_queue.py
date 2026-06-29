"""
Day 39 — asyncio.Queue：生产者-消费者模式
=========================================
对于前端工程师：
  Python  asyncio.Queue  ≈  JS 没有直接等价物
  最接近的是  async 队列库 或 MessageChannel
  但 JS 单线程通常用事件 + 数组模拟即可

场景：多个 worker 并发处理 URL 列表（爬虫 / 批量下载）
"""

import asyncio
import random


# ── 模拟数据抓取 ──
async def fetch_url(url: str, worker_id: int) -> str:
    """模拟异步 HTTP 请求（sleep 随机时间）"""
    delay = random.uniform(0.3, 1.2)
    await asyncio.sleep(delay)
    # 模拟部分请求失败
    if random.random() < 0.15:  # 15% 概率失败
        raise RuntimeError(f"请求失败: {url}")
    return f"[Worker-{worker_id}] 已抓取 {url} (耗时 {delay:.2f}s)"


# ── 消费者 Worker ──
async def worker(
    worker_id: int,
    queue: asyncio.Queue,
    results: list,
):
    """从队列中取出 URL 并处理，直到收到停止信号"""
    while True:
        url = await queue.get()   # 阻塞直到队列有数据

        # ── 停止信号 ──
        if url is None:
            queue.task_done()
            print(f"  [Worker-{worker_id}] 收到停止信号，退出")
            break

        # ── 处理 URL ──
        try:
            result = await fetch_url(url, worker_id)
            results.append(result)
            print(f"  {result}")
        except RuntimeError as e:
            results.append(f"[Worker-{worker_id}] {e}")
            print(f"  [Worker-{worker_id}] ⚠️ {e}")

        queue.task_done()  # 通知队列当前任务完成


# ── 生产者：往队列放数据 ──
async def main():
    print("=" * 60)
    print("asyncio.Queue 生产者-消费者模式")
    print("3 个 worker 并发处理 10 个 URL 任务")
    print("=" * 60)
    print()

    # 创建队列
    queue: asyncio.Queue = asyncio.Queue(maxsize=5)  # 最多缓存 5 个
    results: list = []

    # 模拟 URL 列表
    urls = [
        f"https://api.example.com/data/{i}"
        for i in range(1, 11)
    ]

    # ── 创建 3 个 worker ──
    # JS 版没有直接等价物，通常用有限并发的 Promise 池模拟
    #   async function worker(id, iterator) { ... }
    #   const workers = Array(3).fill(null).map((_, i) => worker(i, urlIterator));
    workers = [
        asyncio.create_task(worker(i + 1, queue, results))
        for i in range(3)
    ]

    # ── 生产者：放入 URL ──
    # 如果队列满，put() 会阻塞等待
    for url in urls:
        await queue.put(url)
        print(f"  [生产者] 放入 {url}  (队列大小: {queue.qsize()})")

    # ── 等待所有任务完成 ──
    await queue.join()

    # ── 发送停止信号给每个 worker ──
    for _ in workers:
        await queue.put(None)

    # ── 等待所有 worker 退出 ──
    await asyncio.gather(*workers)

    print()
    print("--- 最终结果 ---")
    for r in results:
        print(f"  {r}")
    print(f"\n总计完成: {len(results)} 个 (含失败)")
    print()
    print("💡 设计要点:")
    print("   1. maxsize 控制背压，防止生产者过快")
    print("   2. None 作为毒丸信号（poison pill）优雅关闭 worker")
    print("   3. task_done() + join() 确保所有任务完成")


if __name__ == "__main__":
    asyncio.run(main())
