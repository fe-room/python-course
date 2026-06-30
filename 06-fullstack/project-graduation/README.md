# 毕业项目：完整博客系统

## 一、项目概述

本项目要求你从零构建一个完整的博客系统，涵盖后端开发、数据库设计、认证授权、API 设计以及容器化部署等全栈开发核心技能。

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 数据库 | SQLite (开发) / PostgreSQL (生产) |
| 认证 | JWT (python-jose) |
| 密码哈希 | passlib + bcrypt |
| ORM | SQLAlchemy |
| 部署 | Docker + Render |

### 学习目标

- 掌握 FastAPI 项目结构与路由组织
- 掌握 SQLAlchemy 模型设计与迁移
- 掌握 JWT 认证流程与中间件
- 掌握 RESTful API 设计规范
- 掌握 Docker 镜像构建与部署

---

## 二、分阶段需求

### Phase 1：项目搭建 + 数据库模型

**目标**：搭建项目骨架，定义数据库模型

**需求清单**：

1. 按上方目录结构创建所有文件
2. 配置 `requirements.txt`，包含以下依赖：
   - fastapi, uvicorn, sqlalchemy, python-jose, passlib, bcrypt, python-multipart, pydantic, pytest, httpx
3. 实现 `database.py` — SQLite 连接配置
4. 实现 `models.py` — 三个模型：

```python
# User 模型
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Article 模型
class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    author = relationship("User", back_populates="articles")
    category = relationship("Category", back_populates="articles")

# Category 模型
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    articles = relationship("Article", back_populates="category")
```

### Phase 2：认证系统

**目标**：实现用户注册、登录与 JWT 令牌验证

**需求清单**：

1. 实现 `auth.py` — 包含：

```python
# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# JWT 令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

2. 实现 `routers/users.py` — 两个端点：
   - `POST /api/register` — 创建用户，返回用户信息
   - `POST /api/login` — 验证凭证，返回 JWT token

3. 实现 `dependencies.py` — 依赖注入函数：

```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = verify_token(token)
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user
```

### Phase 3：文章 CRUD

**目标**：实现文章的增删改查，带权限控制

**需求清单**：

1. 实现 `routers/articles.py` — 五个端点：

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/articles` | 文章列表（支持分页） | 公开 |
| GET | `/api/articles/{id}` | 文章详情 | 公开 |
| POST | `/api/articles` | 创建文章 | 登录用户 |
| PUT | `/api/articles/{id}` | 更新文章 | 作者本人 |
| DELETE | `/api/articles/{id}` | 删除文章 | 作者本人/管理员 |

2. 权限校验规则：
   - 创建：任何登录用户皆可
   - 更新/删除：仅文章作者可操作
   - 非公开文章：仅作者可见

### Phase 4：分类管理 + 筛选

**目标**：实现分类 CRUD 以及按分类筛选文章

**需求清单**：

1. 实现 `routers/categories.py` — 四个端点：

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/categories` | 分类列表 | 公开 |
| POST | `/api/categories` | 创建分类 | 登录用户 |
| PUT | `/api/categories/{id}` | 更新分类 | 登录用户 |
| DELETE | `/api/categories/{id}` | 删除分类 | 管理员 |

2. 文章列表端点增加筛选参数：
   ```
   GET /api/articles?category_id=1&published=true&search=keyword
   ```

### Phase 5：Docker + 部署

**目标**：容器化并部署到云端

**需求清单**：

1. 编写 `Dockerfile`：

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. 编写 `.env.example`：

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./blog.db
```

3. 本地构建并运行验证：

```bash
docker build -t blog-backend .
docker run -p 8000:8000 blog-backend
```

4. 部署到 Render（参考 Day 81 内容）

---

## 三、项目结构模板

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── database.py          # 数据库连接与会话
│   ├── models.py            # SQLAlchemy 模型
│   ├── schemas.py           # Pydantic 请求/响应模型
│   ├── auth.py              # 密码哈希 + JWT
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── articles.py      # 文章 CRUD
│   │   ├── categories.py    # 分类管理
│   │   └── users.py         # 注册 + 登录
│   └── dependencies.py      # 依赖注入（获取当前用户等）
├── requirements.txt
├── Dockerfile
├── .env.example
└── tests/
    └── test_api.py
```

---

## 四、API 端点参考

| 方法 | 路径 | 请求体 | 响应 | 说明 |
|------|------|--------|------|------|
| POST | `/api/register` | `{"username", "email", "password"}` | `{"id", "username", "email"}` | 注册 |
| POST | `/api/login` | `{"username", "password"}` | `{"access_token", "token_type"}` | 登录获取 token |
| GET | `/api/articles` | — | `[{"id", "title", ...}]` | 文章列表 |
| GET | `/api/articles/{id}` | — | `{"id", "title", "content", ...}` | 文章详情 |
| POST | `/api/articles` | `{"title", "content", "category_id"}` | `{"id", "title", ...}` | 创建文章 |
| PUT | `/api/articles/{id}` | `{"title", "content", "published"}` | `{"id", "title", ...}` | 更新文章 |
| DELETE | `/api/articles/{id}` | — | `{"message": "Deleted"}` | 删除文章 |
| GET | `/api/categories` | — | `[{"id", "name", ...}]` | 分类列表 |
| POST | `/api/categories` | `{"name", "description"}` | `{"id", "name", ...}` | 创建分类 |
| PUT | `/api/categories/{id}` | `{"name", "description"}` | `{"id", "name", ...}` | 更新分类 |
| DELETE | `/api/categories/{id}` | — | `{"message": "Deleted"}` | 删除分类 |

### 认证方式

所有受保护的端点在请求头中携带 token：

```
Authorization: Bearer <your-jwt-token>
```

---

## 五、推荐前端技术栈

### 方案 A：React

| 工具 | 用途 |
|------|------|
| React + Vite | 前端框架 |
| React Router | 路由 |
| Axios | HTTP 请求 |
| Tailwind CSS / Ant Design | UI 组件 |
| React Query / SWR | 数据请求缓存 |

### 方案 B：Vue

| 工具 | 用途 |
|------|------|
| Vue 3 + Vite | 前端框架 |
| Vue Router | 路由 |
| Pinia | 状态管理 |
| Axios | HTTP 请求 |
| Element Plus / Naive UI | UI 组件 |

### 前后端联调要点

1. 开发时配置 Vite 代理转发 API 请求
2. 登录后将 token 存储在 `localStorage`
3. 使用 axios 拦截器自动附加 `Authorization` 头
4. 处理 401 响应时自动跳转到登录页

---

## 六、自查清单

提交前逐项检查：

### 基础功能 (40%)

- [ ] 项目结构完整，无缺失文件
- [ ] `GET /api/articles` 返回文章列表
- [ ] `POST /api/register` 可创建用户
- [ ] `POST /api/login` 返回 JWT token
- [ ] 使用正确 token 可创建文章
- [ ] 使用错误/过期 token 返回 401

### 进阶功能 (30%)

- [ ] 仅作者可更新/删除自己的文章
- [ ] 分类的增删改查正常
- [ ] 可按分类筛选文章列表
- [ ] 支持分页参数 (`page`, `per_page`)

### 代码质量 (20%)

- [ ] 使用了 Pydantic schemas 做输入校验
- [ ] 密码使用 bcrypt 哈希存储
- [ ] 敏感配置通过环境变量读取
- [ ] API 返回统一的错误格式

### 部署 (10%)

- [ ] Dockerfile 可成功构建
- [ ] 容器启动后 API 可正常访问
- [ ] 在 Render 上成功部署