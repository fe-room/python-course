"""
Day 1: pip 与依赖管理入门
===========================

这是一个教学演示脚本，展示 Python 项目中 pip 和 requirements.txt 的基本用法。
你可以直接运行此脚本，它会打印出各个概念的说明和示例。

运行方式：
    python day1_venv.py
"""


def section(title: str) -> None:
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ============================================================================
# 1. requirements.txt 格式说明
# ============================================================================

section("1. requirements.txt 格式")

print("""
requirements.txt 是一个文本文件，列出项目所需的所有 Python 包及其版本。

基本格式：
    package_name          # 安装最新版本（不推荐）
    package_name==1.2.3   # 安装指定版本（推荐）
    package_name>=1.2.3   # 安装不低于某个版本
    package_name~=1.2.3   # 兼容版本（>=1.2.3, ==1.2.*）
    package_name>=1.0,<2.0  # 版本范围

一个典型的 requirements.txt 文件内容如下：
""")

example_requirements = """fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.30
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
pydantic==2.7.0
"""

print(example_requirements)

print("""
版本锁定 (==) 确保所有开发者和部署环境使用完全相同的包版本，
避免"在我电脑上能运行"的问题。
""")


# ============================================================================
# 2. pip freeze 概念演示
# ============================================================================

section("2. pip freeze 演示")

print("""
pip freeze 命令会列出当前 Python 环境中所有已安装的包及其版本。
这是生成 requirements.txt 最常用的方式。

运行以下命令即可生成：
    pip freeze > requirements.txt

pip freeze 输出的内容大致如下所示（运行本脚本时是模拟输出）：
""")

# 模拟 pip freeze 输出
fake_freeze = [
    "annotated-types==0.7.0",
    "anyio==4.4.0",
    "bcrypt==4.1.3",
    "certifi==2024.7.4",
    "click==8.1.7",
    "fastapi==0.115.0",
    "h11==0.14.0",
    "idna==3.7",
    "passlib==1.7.4",
    "pydantic==2.7.0",
    "pydantic-core==2.18.2",
    "python-jose==3.3.0",
    "python-multipart==0.0.9",
    "PyYAML==6.0.1",
    "sniffio==1.3.1",
    "SQLAlchemy==2.0.30",
    "starlette==0.38.0",
    "typing_extensions==4.12.2",
    "uvicorn==0.30.0",
]

for line in fake_freeze:
    print(f"    {line}")


# ============================================================================
# 3. 从 requirements.txt 安装
# ============================================================================

section("3. 从 requirements.txt 安装")

print("""
安装项目中所有依赖：
    pip install -r requirements.txt

常用参数说明：
    pip install -r requirements.txt
        -r  表示从文件中读取依赖列表

    pip install -r requirements.txt --no-cache-dir
        --no-cache-dir  不使用本地缓存，从远程重新下载

    pip install -r requirements.txt -q
        -q  安静模式，减少输出信息

更新所有依赖到最新兼容版本：
    pip install --upgrade -r requirements.txt

检查依赖冲突：
    pip check
""")


# ============================================================================
# 4. 开发依赖 vs 生产依赖
# ============================================================================

section("4. 开发依赖 vs 生产依赖")

print("""
在实际项目中，我们通常将依赖分为两类：

--- 生产依赖 (production dependencies) ---
    应用运行时必需的包。
    例如：FastAPI、SQLAlchemy、Pydantic

--- 开发依赖 (dev dependencies) ---
    仅在开发和测试阶段使用的包。
    例如：pytest、black、mypy、ruff

两种常见的管理方式：
""")

print("方式一：使用两个文件")
print("""
    requirements.txt        # 生产依赖
        fastapi==0.115.0
        uvicorn==0.30.0
        sqlalchemy==2.0.30

    requirements-dev.txt    # 开发依赖（包含生产依赖）
        -r requirements.txt
        pytest==8.0.0
        pytest-cov==5.0.0
        black==24.4.0
        ruff==0.5.0
""")

print("方式二：使用单文件 + 分组标记（pip >= 21.3）")
print("""
    requirements.txt
        fastapi==0.115.0
        uvicorn==0.30.0
        sqlalchemy==2.0.30
        pytest==8.0.0          # --exclude 或在 dev 环境安装时手动移除

    # 或者使用 pip 的 --group 特性
    pip install -r requirements.txt  # 仅安装生产依赖
""")

print("在实际项目中，推荐方式一（两个文件），清晰明了。", end="\n\n")


# ============================================================================
# 5. 虚拟环境最佳实践
# ============================================================================

section("5. 虚拟环境最佳实践")

print("""
强烈建议每个项目使用独立的虚拟环境。

Python 官方推荐的方式：

    # 创建虚拟环境
    python -m venv .venv

    # 激活虚拟环境
    # macOS / Linux:
    source .venv/bin/activate

    # Windows:
    .venv\\Scripts\\activate

    # 激活后在虚拟环境中安装依赖
    pip install -r requirements.txt

    # 退出虚拟环境
    deactivate

最佳实践总结：
    1. 每个项目一个 .venv
    2. .venv 目录加入 .gitignore
    3. 始终在激活的虚拟环境中安装依赖
    4. 使用 requirements.txt 锁定版本
    5. 定期更新依赖（特别是安全更新）
""", end="\n\n")

print("""
快速工作流：
    1. git clone <project>
    2. python -m venv .venv
    3. source .venv/bin/activate
    4. pip install -r requirements.txt
    5. 开始编码！
""")


# ============================================================================
# 6. 常用 pip 命令速查
# ============================================================================

section("6. pip 命令速查")

print("""
    pip --version                   # 查看 pip 版本
    pip list                        # 列出已安装的包
    pip list --outdated            # 列出可更新的包
    pip show <package>             # 查看包详情
    pip install <package>          # 安装包
    pip install <package>==x.y.z   # 安装指定版本
    pip uninstall <package>        # 卸载包
    pip freeze                     # 列出已安装包及其版本
    pip freeze > requirements.txt  # 生成依赖文件
    pip install -r requirements.txt  # 从文件安装
    pip check                      # 检查依赖冲突
    pip cache purge                # 清除缓存
""", end="\n\n")


# ============================================================================
# 脚本入口
# ============================================================================

if __name__ == "__main__":
    print()
    print("  欢迎学习 Python 依赖管理！")
    print("  本脚本仅用于教学演示，不执行任何实际的 pip 命令。")
    print("  请阅读输出的说明文字来了解 pip 和 requirements.txt 的用法。")
    print()