"""
Day 62 - Alembic：数据库迁移工具
================================
Alembic 是 SQLAlchemy 的数据库迁移工具，用于管理数据库 schema 的版本变更。
类似 Git 管理代码版本，Alembic 管理数据库结构的版本。

安装：pip install alembic

运行方式：# 这不是一个可执行脚本，而是说明文档
          # 请按下方步骤在终端执行命令
"""

# ============================================================
# 第一步：初始化 Alembic
# ============================================================
"""
在项目根目录执行：

    $ alembic init alembic

这会创建以下目录结构：
    project/
    ├── alembic/                   # 迁移脚本目录
    │   ├── env.py                 # 环境配置（关键！）
    │   ├── script.py.mako         # 迁移脚本模板
    │   └── versions/              # 版本迁移文件
    └── alembic.ini               # Alembic 配置文件
"""

# ============================================================
# 第二步：配置 env.py
# ============================================================
"""
编辑 alembic/env.py，这是最关键的一步：
需要告诉 Alembic 你的 SQLAlchemy 模型在哪里，以及使用哪个数据库。

下方是 env.py 的标准配置模板：
"""

ENV_PY_TEMPLATE = """
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

# 将项目根目录加入 Python 路径，确保能导入你的模型
sys.path.append(str(Path(__file__).parent.parent))

from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool

# 导入你的 SQLAlchemy 模型基类
# 重要：必须导入模型模块，否则 autogenerate 检测不到表变化
from your_project.models import Base  # ← 修改为你的实际路径

# Alembic 配置对象
config = context.config

# 设置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 元数据 — autogenerate 依赖这个来检测变化
target_metadata = Base.metadata

# 数据库 URL（也可以在 alembic.ini 中设置）
# 格式：sqlalchemy.url = sqlite:///app.db
# 格式：sqlalchemy.url = postgresql://user:pass@localhost/dbname
# 格式：sqlalchemy.url = mysql://user:pass@localhost/dbname

def run_migrations_offline():
    \"\"\"离线模式：生成 SQL 脚本但不执行\"\"\"
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    \"\"\"在线模式：直接连接数据库执行迁移\"\"\"
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""

# ============================================================
# 第三步：修改 alembic.ini
# ============================================================
"""
编辑 alembic.ini，设置数据库连接：

    sqlalchemy.url = sqlite:///app.db
"""

# ============================================================
# 常见命令（在终端执行）
# ============================================================

COMMANDS = """
┌────────────────────────────────────────────────────────────────┐
│  Alembic 常用命令                                             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  # 1. 创建自动迁移脚本（基于模型和数据库的差异自动生成）      │
│  $ alembic revision --autogenerate -m "add users table"       │
│                                                                │
│  # 2. 查看当前版本                                            │
│  $ alembic current                                             │
│                                                                │
│  # 3. 查看迁移历史                                            │
│  $ alembic history                                             │
│                                                                │
│  # 4. 升级到最新版本                                          │
│  $ alembic upgrade head                                        │
│                                                                │
│  # 5. 升级指定版本                                            │
│  $ alembic upgrade abc123def                                   │
│                                                                │
│  # 6. 升级 N 个版本                                            │
│  $ alembic upgrade +2                                          │
│                                                                │
│  # 7. 回滚 1 个版本                                            │
│  $ alembic downgrade -1                                        │
│                                                                │
│  # 8. 回滚到指定版本                                          │
│  $ alembic downgrade abc123def                                 │
│                                                                │
│  # 9. 生成 SQL 脚本（不执行，离线模式）                       │
│  $ alembic upgrade head --sql                                  │
│                                                                │
│  # 10. 查看当前版本号                                          │
│  $ alembic heads                                               │
│                                                                │
└────────────────────────────────────────────────────────────────┘
"""

# ============================================================
# 迁移脚本示例（自动生成的 versions/ 文件）
# ============================================================

MIGRATION_EXAMPLE = """
# 这是自动生成的迁移脚本示例
# 文件路径：alembic/versions/abc123def_add_users_table.py

\"\"\"add users table

Revision ID: abc123def
Revises:
Create Date: 2024-06-29 10:30:00.000000
\"\"\"

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by alembic.
revision: str = 'abc123def'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    \"\"\"升级：应用变更\"\"\"
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )


def downgrade() -> None:
    \"\"\"降级：撤销变更\"\"\"
    op.drop_table('users')
"""

# ============================================================
# 完整工作流程
# ============================================================

WORKFLOW = """
┌────────────────────────────────────────────────────────────────┐
│  Alembic 标准工作流程                                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. 修改 Python 模型类（添加字段、修改类型等）                │
│     → 例如：在 User 模型中添加 age 字段                       │
│                                                                │
│  2. 生成迁移脚本                                              │
│     $ alembic revision --autogenerate -m "add age to users"   │
│     → 自动检测模型与数据库的差异并生成迁移脚本               │
│                                                                │
│  3. 审查生成的迁移脚本                                        │
│     → 检查 alembic/versions/ 下的新文件                       │
│     → 确认 upgrade() 和 downgrade() 逻辑正确                 │
│                                                                │
│  4. 应用迁移                                                  │
│     $ alembic upgrade head                                    │
│     → 将变更应用到数据库                                     │
│                                                                │
│  5. （可选）回滚                                              │
│     $ alembic downgrade -1                                    │
│     → 撤销上一次迁移                                         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
"""


# ============================================================
# main() — 打印所有说明
# ============================================================

def main():
    print("=" * 65)
    print("  Day 62 - Alembic 数据库迁移工具")
    print("  这是一个 README 风格的说明文件，不是可执行脚本。")
    print("=" * 65)

    print("\n" + "=" * 65)
    print("  1. 安装 Alembic")
    print("=" * 65)
    print("""
    pip install alembic
    """)

    print("=" * 65)
    print("  2. 初始化")
    print("=" * 65)
    print("""
    alembic init alembic
    """)

    print("=" * 65)
    print("  3. 配置 env.py（关键步骤）")
    print("=" * 65)
    print("""
    在 alembic/env.py 中：
      - 导入你的 Base（from your_project.models import Base）
      - 设置 target_metadata = Base.metadata
      - 可选：修改 sqlalchemy.url 连接字符串
    """)

    print("=" * 65)
    print("  4. 常用命令速查")
    print("=" * 65)
    print(COMMANDS)

    print("=" * 65)
    print("  5. 工作流程")
    print("=" * 65)
    print(WORKFLOW)

    print("=" * 65)
    print("  6. 注意事项")
    print("=" * 65)
    print("""
    [1] autogenerate 只能检测常见变更：
        添加/删除表、添加/删除列、修改列类型/nullable
        不支持：表重命名、列重命名、索引变更

    [2] 列重命名需要手动编写迁移脚本：
        op.alter_column('users', 'old_name', new_column_name='new_name')

    [3] 团队协作时，每个人都需要执行 alembic upgrade head
        确保数据库 schema 与代码保持一致

    [4] 不要手动修改已发布的迁移脚本版本号！
        如果迁移出错，应该创建新的修复迁移，而不是修改已有记录
    """)


if __name__ == "__main__":
    main()
