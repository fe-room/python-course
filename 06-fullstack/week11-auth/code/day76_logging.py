"""
day76_logging.py — 日志系统配置（Logging Configuration）
=========================================================
知识点：
  1. logging.basicConfig     — 基础日志配置
  2. FileHandler             — 将日志写入文件
  3. StreamHandler           — 将日志输出到控制台
  4. 结构化日志格式          — 包含时间戳、级别、模块名、行号等
  5. 日志级别                — DEBUG < INFO < WARNING < ERROR < CRITICAL

运行方式：
  python day76_logging.py

生产建议：
  - 生产环境建议使用 JSON 格式的结构化日志，方便日志聚合系统（ELK、Datadog 等）
  - 日志文件应配置日志轮转（RotatingFileHandler），防止磁盘占满
  - 敏感信息（密码、Token）绝不要记录到日志中
"""

import logging
import sys
from pathlib import Path

# ------------------------------------------------------------------
# 日志配置常量
# ------------------------------------------------------------------
LOG_DIR = Path(__file__).parent / "logs"          # 日志文件存放目录
LOG_FILE = LOG_DIR / "app.log"                     # 日志文件路径
LOG_LEVEL = logging.DEBUG                          # 开发阶段用 DEBUG，生产用 INFO
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
# 格式说明:
#   %(asctime)s     — 时间戳 (2025-01-15 10:30:00,123)
#   %(levelname)-8s — 日志级别，左对齐，宽度 8 (INFO   )
#   %(name)s        — Logger 名称（通常是模块名）
#   %(lineno)d      — 代码行号
#   %(message)s     — 日志内容

# 时间格式（可选，默认是 ISO 格式）
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_file: str = LOG_FILE,
    level: int = LOG_LEVEL,
    console: bool = True,
) -> logging.Logger:
    """
    配置全局日志系统。

    创建 logs 目录（如不存在），配置 FileHandler 和可选的 StreamHandler。

    Parameters
    ----------
    log_file : str
        日志文件的路径。
    level : int
        日志级别（logging.DEBUG / INFO / WARNING / ERROR / CRITICAL）。
    console : bool
        是否同时输出到控制台（默认 True）。

    Returns
    -------
    logging.Logger
        配置好的根 Logger 实例。

    Examples
    --------
    >>> logger = setup_logging()
    >>> logger.info("系统启动 System started")
    """
    # 1. 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # 2. 创建 formatter（格式化器）
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # 3. 创建 FileHandler（文件处理器）
    #    encoding="utf-8" 确保中文日志不乱码
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # 4. 获取根 Logger，清空已有处理器，添加新的
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清除已有处理器（避免重复添加）
    root_logger.handlers.clear()

    # 添加 FileHandler
    root_logger.addHandler(file_handler)

    # 5. 可选：添加 StreamHandler（控制台输出）
    if console:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    获取一个命名的 Logger 实例。

    推荐在每个模块中使用:
        logger = get_logger(__name__)

    Parameters
    ----------
    name : str
        Logger 名称，通常传入 __name__。

    Returns
    -------
    logging.Logger
    """
    return logging.getLogger(name)


# ------------------------------------------------------------------
# 日志使用示例
# ------------------------------------------------------------------
class UserService:
    """模拟用户服务的日志使用"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def create_user(self, username: str) -> dict:
        """创建用户（模拟）"""
        self.logger.info("正在创建用户 Creating user: %s", username)

        # 模拟业务逻辑
        if len(username) < 3:
            self.logger.warning("用户名过短 Username too short: %s", username)
            raise ValueError("用户名至少需要 3 个字符")

        user = {"id": 123, "username": username, "role": "user"}
        self.logger.info("用户创建成功 User created: %s", user)
        return user

    def delete_user(self, user_id: int):
        """删除用户（模拟）"""
        self.logger.warning("删除用户 Delete user ID: %d", user_id)
        # 实际项目中此处执行删除操作
        self.logger.info("用户已删除 User deleted: %d", user_id)


# ------------------------------------------------------------------
# 直接运行演示
# ------------------------------------------------------------------
if __name__ == "__main__":
    # 1. 配置日志
    logger = setup_logging()

    print("=" * 60)
    print("日志系统演示 Logging Demo")
    print("=" * 60)
    print(f"\n日志文件路径: {LOG_FILE}")
    print(f"日志级别    : {logging.getLevelName(LOG_LEVEL)}")
    print("\n--- 开始记录日志 ---\n")

    # 2. 演示不同日志级别
    logger.debug("这是一条 DEBUG 日志（开发调试用）")
    logger.info("这是一条 INFO 日志（正常运行信息）")
    logger.warning("这是一条 WARNING 日志（需要注意但不影响运行）")
    logger.error("这是一条 ERROR 日志（出错了但程序继续运行）")
    logger.critical("这是一条 CRITICAL 日志（严重错误，可能需立即处理）")

    print("\n--- 模拟业务场景 ---\n")

    # 3. 模拟业务日志
    service = UserService()

    try:
        service.create_user("alice")     # 应该成功
        service.create_user("ab")        # 应该失败（用户名太短）
    except ValueError as e:
        logger.error("业务异常 Business error: %s", e)

    service.delete_user(42)

    print(f"\n--- 日志已写入 {LOG_FILE} ---")
    print("\n提示：打开 logs/app.log 查看完整的日志记录")

    # 4. 演示命名 Logger
    auth_logger = get_logger("auth")
    auth_logger.info("用户登录成功 User login successful: admin")
    auth_logger.warning("登录失败 Login failed: 连续 5 次密码错误")
