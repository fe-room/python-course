"""
第 30 天：yield from —— 委托给子生成器
========================================
yield from 可以将一个生成器"委托"给另一个生成器，
简化嵌套生成器的编写。

对于前端工程师：
- yield from 类似 JS 中的 yield* 表达式
  function* gen1() { yield* gen2(); }
- 注意：yield from 不只是语法糖，它还建立了双向通信通道
"""

import os


# ---------------------------------------------------------------
# 1. yield from 基本用法
# ---------------------------------------------------------------
def sub_generator():
    """子生成器：产生三个颜色。"""
    yield "红"
    yield "黄"
    yield "蓝"


def main_generator_without_yield_from():
    """不使用 yield from —— 手动委托。"""
    for value in sub_generator():
        yield value


def main_generator_with_yield_from():
    """使用 yield from —— 简洁委托。"""
    # 这等价于上面的 for 循环，但更简洁
    yield from sub_generator()
    # yield from 会自动处理子生成器的迭代和 StopIteration


def demo_yield_from_basic():
    """对比两种方式。"""
    print("--- yield from 基本用法 ---")

    print("不使用 yield from:", list(main_generator_without_yield_from()))
    print("使用 yield from:   ", list(main_generator_with_yield_from()))


# ---------------------------------------------------------------
# 2. yield from 连接多个子生成器
# ---------------------------------------------------------------
def gen_numbers():
    """产生数字 1-3。"""
    yield 1
    yield 2
    yield 3


def gen_letters():
    """产生字母 A-C。"""
    yield "A"
    yield "B"
    yield "C"


def combined_generator():
    """通过 yield from 将多个子生成器串联起来。"""
    yield from gen_numbers()
    yield "--- 分割线 ---"
    yield from gen_letters()


def demo_combine():
    print("\n--- yield from 串联多个生成器 ---")
    print("合并结果:", list(combined_generator()))


# ---------------------------------------------------------------
# 3. 读取多个 CSV/日志文件（实际应用场景）
# ---------------------------------------------------------------
def read_lines_from_file(file_path: str):
    """子生成器：读取单个文件的所有行。"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:  # 跳过空行
                    yield line
    except FileNotFoundError:
        yield f"[文件未找到: {file_path}]"


def read_multiple_files(file_paths: list):
    """
    读取多个文件的全部行。
    使用 yield from 将每个文件的读取委托给子生成器。

    如果不使用 yield from，你需要嵌套两层循环：
        for path in file_paths:
            for line in read_lines_from_file(path):
                yield line
    """
    for path in file_paths:
        # 生成文件名标记，方便区分来源
        yield f">>> 文件: {path}"
        yield from read_lines_from_file(path)
        yield ""  # 文件间空行


def demo_read_multiple_files():
    """演示读取多个文件。"""
    import tempfile

    print("\n--- 读取多个文件（模拟） ---")

    # 创建临时文件
    tmp_files = []
    contents = [
        ["姓名,年龄,城市", "张三,28,北京", "李四,32,上海"],
        ["商品,价格", "苹果,5.5", "香蕉,3.0"],
        ["日志: 系统启动", "日志: 连接成功"],
    ]

    for idx, lines in enumerate(contents):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8",
            suffix=f"_file{idx}.txt", delete=False
        )
        for line in lines:
            tmp.write(line + "\n")
        tmp.close()
        tmp_files.append(tmp.name)

    # 用 yield from 读取所有文件
    print("合并读取所有文件:")
    for line in read_multiple_files(tmp_files):
        if line:
            print(f"  {line}")

    # 清理
    for f in tmp_files:
        os.unlink(f)


# ---------------------------------------------------------------
# 4. yield from 与 send() 的双向通信（进阶）
# ---------------------------------------------------------------
def sub_gen_echo():
    """
    子生成器：回显收到的值。
    注意：yield 既可以产出值，也可以接收值（通过 send()）。
    """
    received = yield "子生成器就绪"  # 第一次产出
    while True:
        received = yield f"子生成器收到: {received}"


def delegating_gen():
    """
    委托生成器。
    yield from 会在 子生成器 和 调用者 之间建立双向通道。
    """
    # yield from 会把调用者的 send() 直接传递给子生成器
    result = yield from sub_gen_echo()
    # 当子生成器结束时，result 会收到返回值
    return result


def demo_bidirectional():
    """
    演示 yield from 的双向通信。

    前端类比：
    就像 React 中父组件通过 props 传数据给子组件，
    子组件通过回调传回数据 —— yield from 在这里是
    调用者 <-> 委托生成器 <-> 子生成器 的全双工通道。
    """
    print("\n--- yield from 双向通信（send） ---")

    gen = delegating_gen()

    # 启动生成器（首次调用 next 或 send(None)）
    msg = next(gen)
    print(f"调用者收到: {msg}")

    # 通过 send() 向生成器发送值
    # 这个值会穿过委托生成器，直接到达子生成器的 yield 表达式
    msg = gen.send("你好")
    print(f"调用者收到: {msg}")

    msg = gen.send("世界")
    print(f"调用者收到: {msg}")


if __name__ == "__main__":
    print("=" * 55)
    print("第 30 天：yield from —— 委托给子生成器")
    print("=" * 55)

    demo_yield_from_basic()
    demo_combine()
    demo_read_multiple_files()

    print("\n" + "=" * 55)
    print("进阶：yield from 双向通信（send）")
    demo_bidirectional()
