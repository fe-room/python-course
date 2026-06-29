"""
第 32 天：闭包（Closure）
===========================
内部函数捕获外部函数的变量，即使外部函数已经返回。

对于前端工程师（关键对比）：
- Python 的闭包语法和 JS 非常相似
- JS 用 let/const 块级作用域，Python 用 nonlocal 声明
- JS 嵌套函数可以读写外部变量，Python 读取没问题，写入需要 nonlocal

JS 版本对照:
    function makeCounter() {
        let count = 0;
        return function() {
            count++;          // JS 直接捕获 count
            return count;
        };
    }
    const counter = makeCounter();
"""


# ---------------------------------------------------------------
# 1. 基本闭包：计数器
# ---------------------------------------------------------------
def make_counter():
    """
    创建一个计数器，每次调用 +1。

    JS 对比：
        function makeCounter() {
            let count = 0;
            return function() { return ++count; };
        }

    区别：
    - Python 需要 nonlocal 声明 count 不是局部变量
    - JS 不需要任何声明，闭包自动捕获
    """
    count = 0  # 外部函数的局部变量（被内部函数捕获）

    def counter():
        nonlocal count  # 告诉 Python：count 不是这个函数的局部变量
        count += 1
        return count

    return counter


def demo_counter():
    """演示闭包计数器的用法。"""
    print("--- 闭包计数器 ---")

    counter_a = make_counter()  # 创建独立的闭包实例
    counter_b = make_counter()  # 另一个独立实例

    print("counter_a 调用 3 次:")
    for _ in range(3):
        print(f"  {counter_a()}", end=" ")
    print()

    print("counter_b 调用 2 次（独立的 count 变量）:")
    for _ in range(2):
        print(f"  {counter_b()}", end=" ")
    print()

    print("counter_a 再调用 2 次（延续之前的计数）:")
    for _ in range(2):
        print(f"  {counter_a()}", end=" ")
    print()

    # 验证：每个闭包实例维护自己的 count
    print(f"\ncounter_a 的最终值: {counter_a()}")
    print(f"counter_b 的最终值: {counter_b()} (独立于 counter_a)")


# ---------------------------------------------------------------
# 2. 闭包实战：创建固定前缀的问候语生成器
# ---------------------------------------------------------------
def make_greeter(prefix: str):
    """
    创建一个打招呼函数，带有固定的前缀。

    JS 对比：
        function makeGreeter(prefix) {
            return function(name) {
                return `${prefix}, ${name}!`;
            };
        }
    """
    def greeter(name: str) -> str:
        # 这里只读取 prefix（不赋值），所以不需要 nonlocal
        return f"{prefix}, {name}!"

    return greeter


def demo_greeter():
    """演示闭包生成问候语。"""
    print("\n--- 问候语生成器 ---")

    hello_greeter = make_greeter("你好")
    hi_greeter = make_greeter("嗨")

    print(hello_greeter("张三"))  # 你好, 张三!
    print(hi_greeter("李四"))     # 嗨, 李四!
    print(hello_greeter("王五"))  # 你好, 王五!（prefix 仍然是"你好"）


# ---------------------------------------------------------------
# 3. 闭包陷阱（和 JS 一样的坑）
# ---------------------------------------------------------------
def demo_closure_trap():
    """
    闭包捕获的是变量本身，而不是变量的值。
    这在循环中创建闭包时尤其容易出错。

    JS 类比（经典面试题）：
        for (var i = 0; i < 3; i++) {
            setTimeout(function() { console.log(i); }, 100);
        }
        // 输出 3, 3, 3（而不是 0, 1, 2）

    Python 也有同样的问题：
    """
    print("\n--- 闭包陷阱演示 ---")

    # 错误的写法：所有函数共享同一个 i 的最终值
    funcs_wrong = []
    for i in range(3):
        def f():
            return i  # 循环结束后 i = 2，所有 f 都返回 2
        funcs_wrong.append(f)

    results_wrong = [f() for f in funcs_wrong]
    print(f"错误闭包结果: {results_wrong}    (全部返回 {i})")

    # 正确的写法 1：使用默认参数（默认参数在定义时求值）
    funcs_right = []
    for i in range(3):
        def f(x=i):  # 用默认参数"冻结"当前值
            return x
        funcs_right.append(f)

    results_right = [f() for f in funcs_right]
    print(f"正确闭包结果: {results_right}  (默认参数法)")

    # 正确的写法 2：用工厂函数创建新作用域
    def make_f(n):
        def f():
            return n
        return f

    funcs_factory = [make_f(i) for i in range(3)]
    results_factory = [f() for f in funcs_factory]
    print(f"正确闭包结果: {results_factory}  (工厂函数法)")


# ---------------------------------------------------------------
# 4. 闭包内部查看：__closure__ 和 __code__
# ---------------------------------------------------------------
def inspect_closure():
    """
    查看闭包的内部结构。
    每个闭包都包含一个 __closure__ 属性，存储捕获的变量。
    """
    print("\n--- 闭包内省 ---")

    counter = make_counter()
    counter()  # 调用一次

    if counter.__closure__:
        print(f"闭包单元格 (__closure__): {counter.__closure__}")
        for i, cell in enumerate(counter.__closure__):
            print(f"  捕获变量 {i}: {cell.cell_contents}")


if __name__ == "__main__":
    print("=" * 55)
    print("第 32 天：闭包（Closure）")
    print("=" * 55)

    demo_counter()
    demo_greeter()
    demo_closure_trap()
    inspect_closure()
