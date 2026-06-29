"""
Day 36 — 同步 vs 异步：阻塞问题演示
=====================================
对于前端工程师：JS 中同步代码阻塞主线程 => 页面卡顿
Python 中同步 I/O 阻塞当前线程 => CPU 空转等待

对比记忆：
  JS:  alert() / while(true)  → 阻塞主线程
  Py:  time.sleep(n)          → 阻塞当前线程
"""

import time
import datetime


# ── 模拟两个耗时 I/O 任务（比如读取文件 / 请求 API）──

def task_1(name: str) -> str:
    """模拟 I/O 任务，耗时 2 秒"""
    print(f"  [开始] {name}  @ {datetime.datetime.now().strftime('%H:%M:%S')}")
    time.sleep(2)          # 同步阻塞！线程在这里干等
    print(f"  [结束] {name}  @ {datetime.datetime.now().strftime('%H:%M:%S')}")
    return f"{name} 结果"


def task_2(name: str) -> str:
    """模拟另一个 I/O 任务，也耗时 2 秒"""
    print(f"  [开始] {name}  @ {datetime.datetime.now().strftime('%H:%M:%S')}")
    time.sleep(2)
    print(f"  [结束] {name}  @ {datetime.datetime.now().strftime('%H:%M:%S')}")
    return f"{name} 结果"


def main():
    print("=" * 50)
    print("同步版本：两个任务依次执行，总耗时 ≈ 4 秒")
    print("=" * 50)
    print()

    t0 = time.perf_counter()          # 高精度计时

    # ── 同步顺序执行 ──
    # 就像 JS 中的：
    #   const r1 = syncTask("任务A");  // 2s
    #   const r2 = syncTask("任务B");  // 2s
    #   总耗时 ~4s，期间 UI 完全卡死
    r1 = task_1("任务A")
    r2 = task_2("任务B")

    elapsed = time.perf_counter() - t0

    print()
    print(f"结果: r1 = {r1}")
    print(f"结果: r2 = {r2}")
    print(f"总耗时: {elapsed:.2f} 秒  ← 两个 2s 累加，约 4 秒")
    print()
    print("👉 问题：task_2 必须等 task_1 完成才能开始")
    print("👉 这段时间 CPU 无事可做，完全浪费了")


if __name__ == "__main__":
    main()
