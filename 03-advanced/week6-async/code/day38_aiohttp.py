"""
Day 38 — aiohttp：异步 HTTP 请求
================================
对于前端工程师：
  Python  aiohttp.ClientSession  ≈  JS  fetch() + keep-alive
  Python  async with session.get(url)  ≈  JS  await fetch(url)

安装：
  pip install aiohttp

注意：
  - 使用 httpbin.org/delay/N 模拟慢响应（N 秒后返回）
  - 首次运行可能较慢（DNS 解析）
  - 可替换为真实 API
"""

import asyncio
import aiohttp
import datetime


# ── 定义异步 HTTP 请求 ──
# JS 版:
#   async function fetchUrl(url) {
#     const resp = await fetch(url);
#     return resp.json();
#   }

async def fetch_url(session: aiohttp.ClientSession, url: str, index: int) -> dict:
    """发送异步 GET 请求，返回 JSON 数据"""
    print(f"  [请求] #{index}  {url}  @ {datetime.datetime.now().strftime('%H:%M:%S')}")
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            data = await resp.json()
            print(f"  [完成] #{index}  状态码={resp.status}  @ {datetime.datetime.now().strftime('%H:%M:%S')}")
            return data
    except Exception as e:
        print(f"  [失败] #{index}  错误={e}")
        return {"error": str(e), "url": url}


async def main():
    print("=" * 60)
    print("aiohttp 并发请求演示（httpbin.org/delay/N）")
    print("每个端点会延迟 N 秒后返回，观察总耗时 ≈ max(N)")
    print("=" * 60)
    print()

    # 三个不同延迟的端点（0.5s, 1s, 1.5s）
    urls = [
        "https://httpbin.org/delay/0.5",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1.5",
    ]

    t0 = asyncio.get_event_loop().time()

    # ── 使用 ClientSession 作为上下文管理器 ──
    # 类似于 JS 中用一个 keep-alive 连接池发请求
    async with aiohttp.ClientSession() as session:
        # 并发发起所有请求
        # JS 版：
        #   const promises = urls.map(url => fetchUrl(url));
        #   const results = await Promise.all(promises);
        tasks = [
            fetch_url(session, url, idx)
            for idx, url in enumerate(urls, 1)
        ]
        results = await asyncio.gather(*tasks)

    elapsed = asyncio.get_event_loop().time() - t0

    print()
    print("--- 结果汇总 ---")
    for idx, (url, data) in enumerate(zip(urls, results), 1):
        if "error" in data:
            print(f"  #{idx} {url}  => 失败: {data['error']}")
        else:
            print(f"  #{idx} {url}  => 成功 (origin: {data.get('origin', 'N/A')})")

    print(f"\n总耗时: {elapsed:.2f} 秒  ← 并发执行，≈ 最长延迟(1.5s) + 网络开销")
    print()
    print("👉 如果是同步 requests.get()，总耗时会约 0.5+1+1.5 = 3 秒")


if __name__ == "__main__":
    asyncio.run(main())
