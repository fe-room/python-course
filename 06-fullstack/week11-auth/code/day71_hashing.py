"""
day71_hashing.py — 密码哈希（Password Hashing）
================================================
知识点：
  1. 使用 passlib 库的 bcrypt 算法对密码进行哈希
  2. hash_password()        — 将明文密码转为哈希字符串
  3. verify_password()      — 验证明文密码是否匹配哈希

安装依赖：
  pip install "passlib[bcrypt]"

生产建议：
  - bcrypt 的 rounds（轮数）默认 12，可根据安全需求调整
  - 永远不要存储明文密码
  - 哈希过程自动加入随机 salt，无需手动处理
"""

from passlib.context import CryptContext

# ------------------------------------------------------------------
# 创建一个 CryptContext 实例，指定使用 bcrypt 算法
# ------------------------------------------------------------------
# schemes      : 可用的哈希算法列表，第一个为默认
# bcrypt__rounds: bcrypt 的迭代轮数（越大越安全，也越慢）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    对明文密码进行 bcrypt 哈希。

    Parameters
    ----------
    plain_password : str
        用户输入的明文密码。

    Returns
    -------
    str
        哈希后的密码字符串（已包含 salt 和算法信息）。
        示例格式: $2b$12$xxxxxxxxxxxx

    Examples
    --------
    >>> hashed = hash_password("my_secret_123")
    >>> isinstance(hashed, str)
    True
    >>> hashed.startswith("$2b$")
    True
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与给定的哈希值匹配。

    Parameters
    ----------
    plain_password : str
        用户输入的明文密码。
    hashed_password : str
        之前通过 hash_password() 生成的哈希字符串。

    Returns
    -------
    bool
        True  — 密码匹配；
        False — 密码不匹配。

    Examples
    --------
    >>> h = hash_password("hello_world")
    >>> verify_password("hello_world", h)
    True
    >>> verify_password("wrong", h)
    False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ------------------------------------------------------------------
# 如果直接运行此脚本，执行简单的自测（demo）
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("密码哈希演示 Password Hashing Demo")
    print("=" * 50)

    demo_password = "MySecureP@ssw0rd!"
    print(f"\n原始密码: {demo_password}")

    # 1. 哈希
    hashed = hash_password(demo_password)
    print(f"哈希结果: {hashed}")

    # 2. 验证（正确密码）
    ok = verify_password(demo_password, hashed)
    print(f"\n验证正确密码: {ok}")  # 应输出 True

    # 3. 验证（错误密码）
    fail = verify_password("wrong_password", hashed)
    print(f"验证错误密码: {fail}")  # 应输出 False

    # 4. 每次哈希结果不同（salt 随机）
    hashed2 = hash_password(demo_password)
    print(f"\n再次哈希同一密码: {hashed2}")
    print(f"两次哈希是否相同: {hashed == hashed2}")  # 应输出 False
    print(f"但两次都能验证通过: {verify_password(demo_password, hashed2)}")  # True
