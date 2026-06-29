"""
day72_jwt.py — JWT 令牌创建与验证（JSON Web Token）
=====================================================
知识点：
  1. 使用 python-jose 库创建和验证 JWT
  2. create_access_token()  — 根据 user_id 生成带有过期时间的访问令牌
  3. decode_token()         — 解码并验证 JWT 的签名和有效期

安装依赖：
  pip install "python-jose[cryptography]" python-dotenv

生产建议：
  - SECRET_KEY 必须使用环境变量，不要硬编码
  - ALGORITHM 推荐使用 HS256 或 RS256
  - ACCESS_TOKEN_EXPIRE_MINUTES 通常设置为 15-30 分钟
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

# ------------------------------------------------------------------
# 配置常量（生产环境请从环境变量读取）
# ------------------------------------------------------------------
# SECRET_KEY        : 用于签名 JWT 的密钥，必须保密
# ALGORITHM         : 签名算法
# ACCESS_TOKEN_EXPIRE_MINUTES : 访问令牌的有效期（分钟）
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production-use-a-real-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def create_access_token(
    user_id: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    为指定 user_id 创建 JWT 访问令牌。

    Parameters
    ----------
    user_id : str
        用户的唯一标识（可以是字符串或数字的字符串形式）。
    expires_delta : timedelta, optional
        自定义过期时间；若为 None 则使用默认的 ACCESS_TOKEN_EXPIRE_MINUTES。

    Returns
    -------
    str
        编码后的 JWT 字符串。

    Examples
    --------
    >>> token = create_access_token("user_42")
    >>> isinstance(token, str)
    True
    >>> len(token.split(".")) == 3  # JWT 由三个点分隔的部分组成
    True
    """
    # 使用 UTC 时间，避免时区问题
    now = datetime.now(timezone.utc)

    if expires_delta is not None:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # payload（载荷）—— JWT 中携带的数据
    payload = {
        "sub": user_id,  # subject: 令牌主体（通常是用户 ID）
        "iat": now,      # issued at: 签发时间
        "exp": expire,   # expiration: 过期时间
    }

    # 使用密钥和算法对 payload 进行签名，生成 JWT
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_token(token: str) -> dict:
    """
    解码并验证 JWT 令牌。

    Parameters
    ----------
    token : str
        待验证的 JWT 字符串。

    Returns
    -------
    dict
        解码后的 payload 字典（包含 sub, iat, exp 等字段）。

    Raises
    ------
    JWTError
        令牌无效、签名不匹配或已过期时抛出。

    Examples
    --------
    >>> token = create_access_token("user_99")
    >>> payload = decode_token(token)
    >>> payload["sub"]
    'user_99'
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        # 捕获所有 JWT 相关错误（过期、签名无效、格式错误等）
        raise JWTError(f"令牌验证失败 Token validation failed: {e}")


# ------------------------------------------------------------------
# 直接运行时的演示
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("JWT 令牌演示 JWT Token Demo")
    print("=" * 50)

    # 1. 创建令牌
    demo_user_id = "user_001"
    token = create_access_token(demo_user_id)
    print(f"\n用户 ID : {demo_user_id}")
    print(f"JWT     : {token}")
    print(f"令牌由 {len(token.split('.'))} 部分组成")

    # 2. 解码令牌
    decoded = decode_token(token)
    print(f"\n解码结果:")
    print(f"  sub (用户 ID): {decoded['sub']}")
    print(f"  iat (签发时间): {datetime.fromtimestamp(decoded['iat'], tz=timezone.utc)}")
    print(f"  exp (过期时间): {datetime.fromtimestamp(decoded['exp'], tz=timezone.utc)}")

    # 3. 尝试解码伪造的令牌
    print("\n尝试解码伪造令牌...")
    try:
        decode_token("fake.token.here")
    except JWTError as e:
        print(f"  预期错误: {e}")

    # 4. 自定义过期时间
    short_lived = create_access_token("temp", expires_delta=timedelta(seconds=1))
    print(f"\n短期令牌（1 秒过期）: {short_lived}")
