#!/usr/bin/env python3
"""异步图片下载器 — 第 6 周项目

用法:
    python downloader.py urls.txt
    python downloader.py https://example.com/image1.jpg https://example.com/image2.jpg
"""

import asyncio
import aiohttp
import aiofiles
from pathlib import Path
import sys
from dataclasses import dataclass, field
from datetime import datetime
import time


@dataclass
class DownloadResult:
    url: str
    filename: str
    size: int
    success: bool
    error: str = ""


async def download_one(session: aiohttp.ClientSession, url: str, dest: Path, sem: asyncio.Semaphore) -> DownloadResult:
    async with sem:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                resp.raise_for_status()
                content = await resp.read()

                # 从 URL 或 Content-Type 推断扩展名
                ext = Path(url.split("?")[0]).suffix or ".jpg"
                filename = f"{datetime.now().timestamp():.0f}_{hash(url) % 10000}{ext}"
                filepath = dest / filename

                async with aiofiles.open(filepath, "wb") as f:
                    await f.write(content)

                return DownloadResult(url=url, filename=filename, size=len(content), success=True)
        except Exception as e:
            return DownloadResult(url=url, filename="", size=0, success=False, error=str(e))


async def main():
    args = sys.argv[1:]
    if not args:
        print("用法: python downloader.py <url1> <url2> ... 或从文件读取")
        sys.exit(1)

    # 从文件或参数读取 URL
    if len(args) == 1 and Path(args[0]).exists():
        urls = Path(args[0]).read_text().strip().splitlines()
    else:
        urls = args

    dest = Path("downloads")
    dest.mkdir(exist_ok=True)

    sem = asyncio.Semaphore(5)  # 最多 5 个并发

    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [download_one(session, url, dest, sem) for url in urls if url.strip()]
        results = await asyncio.gather(*tasks)

    elapsed = time.time() - start
    success = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    print(f"\n完成！{len(success)} 成功, {len(failed)} 失败, 耗时 {elapsed:.1f}s")
    for r in success:
        print(f"  ✓ {r.filename} ({r.size} bytes)")

    if failed:
        for r in failed:
            print(f"  ✗ {r.url}: {r.error}")


if __name__ == "__main__":
    asyncio.run(main())