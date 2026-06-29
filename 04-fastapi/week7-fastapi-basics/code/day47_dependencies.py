"""
依赖注入 — Depends 的使用
============================
课程: Phase 4, Week 7 — FastAPI 基础
Day 47: 依赖注入 (Dependency Injection)

运行方式:
    uvicorn day47_dependencies:app --reload

测试 URL:
    - GET /items?page=2&size=5        → 使用 Pagination 依赖
    - GET /items                      → 使用默认值
    - GET /admin/secret?token=my-secret-token  → 函数依赖验证
    - GET /admin/secret?token=wrong   → 返回 401
"""

from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status

app = FastAPI(title="依赖注入示例")


# ──────────────────────────────────────────────
# 1. 函数依赖 — 最简单的依赖形式
# ──────────────────────────────────────────────

# 模拟用户认证
VALID_TOKEN = "my-secret-token"


def verify_token(token: str = Query(..., description="认证令牌")):
    """
    函数依赖: 验证 token 是否有效。

    特点:
    - 就是一个普通函数
    - 参数也会被 FastAPI 解析 (因此 Query 同样有效)
    - 返回值会注入到路径函数中
    """
    if token != VALID_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 token",
        )
    return {"user": "admin", "token": token}


@app.get("/admin/secret")
def get_admin_secret(auth: dict = Depends(verify_token)):
    """
    使用 Depends(verify_token) 注入依赖。

    FastAPI 会在调用此函数前先执行 verify_token:
    1. 从查询参数中获取 token
    2. 验证 token 是否匹配
    3. 将返回值注入到 auth 参数中
    """
    return {
        "message": "这是秘密数据",
        "authenticated_user": auth["user"],
    }


# ──────────────────────────────────────────────
# 2. 类依赖 — 可复用、带状态的依赖
# ──────────────────────────────────────────────

class Pagination:
    """
    分页依赖 — 封装分页参数。

    类依赖的好处:
    - 将相关参数组织在一起
    - 可以在 __init__ 中做预处理
    - 可以在方法中提供额外功能
    """

    def __init__(
        self,
        page: int = Query(1, ge=1, description="当前页码"),
        size: int = Query(10, ge=1, le=100, description="每页数量"),
    ):
        self.page = page
        self.size = size
        # 预处理: 计算 offset
        self.offset = (page - 1) * size

    def __call__(self):
        """
        使类实例可调用 (callable)。
        当 Depends(Pagination) 时, FastAPI 实际上会调用
        Pagination() 然后调用实例的 __call__ 方法获取注入值。
        """
        return self


# 模拟数据
fake_items = [{"id": i, "name": f"商品 {i}"} for i in range(1, 101)]


@app.get("/items")
def list_items(pagination: Pagination = Depends(Pagination())):
    """
    使用类依赖进行分页。

    Depends(Pagination()) 会:
    1. 创建 Pagination 实例 → 解析 page, size 参数
    2. 计算 offset
    3. 将实例注入到 pagination 参数中
    """
    items = fake_items[pagination.offset: pagination.offset + pagination.size]
    return {
        "page": pagination.page,
        "size": pagination.size,
        "total": len(fake_items),
        "items": items,
    }


# ──────────────────────────────────────────────
# 3. 依赖的依赖 — 依赖可以嵌套
# ──────────────────────────────────────────────

def get_pagination(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    """另一个分页函数依赖。"""
    return {"page": page, "size": size}


def get_filtered_query(
    q: Optional[str] = Query(None, description="搜索关键词"),
    pagination: dict = Depends(get_pagination),  # 依赖可以嵌套!
):
    """这个依赖本身又依赖了 get_pagination。"""
    return {"q": q, **pagination}


@app.get("/search")
def search(
    filters: dict = Depends(get_filtered_query),
):
    """
    使用嵌套依赖。
    get_filtered_query 内部使用了 get_pagination。
    """
    return {
        "query_params": filters,
        "message": f"搜索: {filters.get('q', '全部')}, "
        f"第 {filters['page']} 页",
    }


# ──────────────────────────────────────────────
# 4. 在路径装饰器中使用 dependencies
# ──────────────────────────────────────────────

def require_admin(token: str = Query(...)):
    """仅管理员可访问的依赖。"""
    if token != "admin-token":
        raise HTTPException(status_code=403, detail="需要管理员权限")


@app.get("/admin/dashboard", dependencies=[Depends(require_admin)])
def admin_dashboard():
    """
    使用 dependencies 参数 (不需要将依赖的返回值注入函数)。

    当某个依赖仅仅是为了"副作用" (如权限验证) 时,
    可以放在 decorator 的 dependencies 参数中。
    """
    return {"message": "欢迎来到管理后台"}