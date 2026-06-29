# Render 部署指南 — FastAPI 应用上云

> 本文档详细说明如何将 FastAPI 应用部署到 Render 云平台。
> Render 是一个现代化的云平台，提供免费的 Web 服务托管。
> 全程使用中文讲解，适合初学者。

---

## 目录

1. [什么是 Render？](#1-什么是-render)
2. [准备工作](#2-准备工作)
3. [项目结构要求](#3-项目结构要求)
4. [第 1 步：创建 requirements.txt](#4-第-1-步创建-requirementstxt)
5. [第 2 步：创建 Dockerfile](#5-第-2-步创建-dockerfile)
6. [第 3 步：推送到 GitHub](#6-第-3-步推送到-github)
7. [第 4 步：在 Render 创建 Web Service](#7-第-4-步在-render-创建-web-service)
8. [第 5 步：配置环境变量](#8-第-5-步配置环境变量)
9. [第 6 步：部署与监控](#9-第-6-步部署与监控)
10. [常见问题](#10-常见问题)

---

## 1. 什么是 Render？

[Render](https://render.com) 是一个云平台即服务（PaaS），类似于 Heroku。它提供：

| 功能 | 免费额度 |
|------|---------|
| Web 服务 | 512 MB 内存，每月 750 小时 |
|  PostgreSQL 数据库 | 1 GB 存储 |
| 自动 HTTPS | 免费 |
| 自定义域名 | 支持 |
| CI/CD | 自动从 GitHub 部署 |

**优势：** 免费、简单、支持 Docker、自动 HTTPS、自动部署。

---

## 2. 准备工作

在开始之前，请确保你已完成以下准备工作：

- [x] 注册 [GitHub](https://github.com) 账号
- [x] 注册 [Render](https://render.com) 账号（可用 GitHub 账号直接登录）
- [x] 本地安装了 Git（`git --version` 检查）
- [x] FastAPI 项目已在本地运行正常
- [x] 已安装 Docker（可选，用于本地测试）

---

## 3. 项目结构要求

部署到 Render 的 FastAPI 项目应具有以下结构：

```
my-fastapi-project/
├── main.py                  # FastAPI 应用入口（必须包含 app 实例）
├── requirements.txt         # Python 依赖列表
├── Dockerfile               # （可选）自定义 Docker 镜像
├── .env                     # （本地）环境变量，不上传到 Git
├── .gitignore               # 忽略不需要的文件
└── app/                     # （可选）应用代码目录
    ├── __init__.py
    ├── models.py
    ├── routes.py
    └── database.py
```

### 入口文件要求（重要）

`main.py` 中必须包含 FastAPI 应用实例：

```python
# main.py
from fastapi import FastAPI

app = FastAPI()  # Render 会寻找这个 app 变量

@app.get("/")
def root():
    return {"message": "Hello from Render!"}
```

---

## 4. 第 1 步：创建 requirements.txt

在项目根目录创建 `requirements.txt`，列出所有依赖包：

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
pydantic==2.9.0
python-multipart==0.0.12
python-dotenv==1.0.1
```

生成当前项目的依赖列表：

```bash
# 方法一：手动导出（推荐）
pip freeze > requirements.txt

# 方法二：使用 pipreqs（只导出项目中实际用到的包）
pip install pipreqs
pipreqs . --force
```

---

## 5. 第 2 步：创建 Dockerfile

在项目根目录创建 `Dockerfile`，定义应用的运行环境：

```dockerfile
# 使用 Python 3.12 slim 镜像（体积小、启动快）
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 先复制依赖文件（利用 Docker 缓存层）
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口（Render 会自动映射）
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 创建 .dockerignore

```dockerignore
__pycache__/
*.pyc
.env
.git/
.gitignore
.DS_Store
logs/
*.md
venv/
.venv/
.idea/
.vscode/
```

### 本地测试 Docker 构建

```bash
# 构建镜像
docker build -t my-fastapi-app .

# 运行容器
docker run -d --name my-app -p 8000:8000 my-fastapi-app

# 测试
curl http://localhost:8000

# 查看日志
docker logs my-app

# 停止容器
docker stop my-app
docker rm my-app
```

---

## 6. 第 3 步：推送到 GitHub

### 初始化 Git 仓库（如果还没有）

```bash
cd my-fastapi-project

# 初始化 Git
git init

# 创建 .gitignore 文件
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.env
.venv/
venv/
.DS_Store
logs/
*.db
EOF

# 添加所有文件并提交
git add .
git commit -m "初始化 FastAPI 项目"
```

### 推送到 GitHub

```bash
# 在 GitHub 上创建一个新仓库（不要勾选 README 和 .gitignore）
# 然后在本地执行：

git remote add origin https://github.com/你的用户名/my-fastapi-project.git
git branch -M main
git push -u origin main
```

---

## 7. 第 4 步：在 Render 创建 Web Service

### 操作步骤

1. **登录 Render**
   - 访问 https://dashboard.render.com
   - 使用 GitHub 账号登录

2. **创建 Web Service**
   - 点击 **"New +"** 按钮
   - 选择 **"Web Service"**

   ![New Web Service](https://render.com/docs/static/new-webservice.png)

3. **连接 GitHub 仓库**
   - 点击 **"Connect GitHub"**
   - 授权 Render 访问你的 GitHub 账号
   - 选择你刚刚推送的仓库
   - 如果仓库没有显示，点击 **"Configure account"** 授权

4. **配置 Web Service**

   | 配置项 | 建议值 |
   |--------|--------|
   | **Name** | `my-fastapi-app`（全局唯一） |
   | **Region** | `Singapore`（亚太地区，延迟最低） |
   | **Branch** | `main` |
   | **Runtime** | `Docker`（使用你的 Dockerfile） |
   | **Build Command** | 留空（Docker 会自动构建） |
   | **Start Command** | 留空（Dockerfile 中已包含 CMD） |
   | **Instance Type** | `Free`（免费版） |

   > **注意：** 如果选择使用 Docker 运行，Render 会自动检测项目根目录的 Dockerfile 并构建镜像。

   如果不想使用 Docker，也可以选择 **Runtime** 为 `Python 3`，然后设置：
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **点击 "Create Web Service"**
   - Render 会自动开始构建和部署
   - 首次构建可能需要 3-5 分钟
   - 可以在日志面板查看实时构建日志

---

## 8. 第 5 步：配置环境变量

### 在 Render Dashboard 中配置

1. 进入你的 Web Service 页面
2. 点击左侧菜单 **"Environment"**
3. 点击 **"Add Environment Variable"**

### 必须配置的环境变量

```env
# Django/FastAPI Secret Key
SECRET_KEY=你的密钥（可以用下面的命令生成）
ENVIRONMENT=production
FRONTEND_URL=https://你的前端域名.onrender.com

# 可选：数据库配置
# DATABASE_URL=postgresql://user:password@host:port/db
# ACCESS_TOKEN_EXPIRE_MINUTES=30
# REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 生成安全的 SECRET_KEY

```python
# 在本地运行 Python，生成安全的密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Render 自动设置的环境变量

Render 会自动设置以下环境变量，你可以在代码中使用：

| 变量名 | 说明 |
|--------|------|
| `PORT` | 服务端口（Render 自动分配） |
| `RENDER` | 值为 `true`（可用于判断是否在 Render 环境） |
| `RENDER_EXTERNAL_URL` | 你的服务的公开 URL |

在代码中检测 Render 环境：

```python
import os

# 判断是否在 Render 上运行
IS_RENDER = os.getenv("RENDER") == "true"

# 使用 Render 分配的端口
port = int(os.getenv("PORT", 8000))
```

---

## 9. 第 6 步：部署与监控

### 自动部署

Render 默认启用自动部署：
- 每次推送代码到 GitHub 的 `main` 分支
- Render 会自动重新构建和部署
- 部署过程中服务不会中断（零停机部署，付费计划支持）

手动部署：在 Dashboard 中点击 **"Manual Deploy"** -> **"Deploy latest commit"**。

### 查看部署状态

- **In Progress** — 正在构建和部署中
- **Live** — 部署成功，服务正在运行
- **Build Failed** — 构建失败（查看日志找原因）

### 查看日志

在 Dashboard 中：
1. 点击 **"Logs"** 标签
2. 可以查看 **Build Log**（构建日志）和 **Runtime Log**（运行日志）
3. 如果出现问题，日志是最好的排查工具

### 测试部署

部署成功后，Render 会提供一个 URL，格式为：
```
https://你的服务名.onrender.com
```

测试方式：

```bash
# 测试根路径
curl https://my-fastapi-app.onrender.com/

# 测试 API 文档
curl https://my-fastapi-app.onrender.com/docs

# 测试健康检查
curl https://my-fastapi-app.onrender.com/health
```

---

## 10. 常见问题

### Q1: 部署后访问返回 503

**原因：** 免费版服务在不活动时会进入休眠（Spindown），再次访问需要 15-30 秒启动时间。

**解决方法：**
- 等待 30 秒后刷新页面
- 使用 UptimeRobot 等监控服务定期 ping（防止休眠）
- 升级到付费计划

### Q2: 构建失败：Could not find a version that satisfies the requirement

**原因：** requirements.txt 中的包版本不存在或冲突。

**解决方法：**
- 使用 `pip install 包名==版本号` 测试兼容性
- 去掉版本号，让 pip 自动选择最新版本
- 确保本地 Python 版本与 Docker 镜像一致

### Q3: CORS 错误（前端调用后端失败）

**原因：** 前端域名不在后端的 CORS 允许列表中。

**解决方法：** 在 Render 的环境变量中设置正确的 `FRONTEND_URL`：

```python
# 在你的 FastAPI 代码中
import os
from fastapi.middleware.cors import CORSMiddleware

origins = [
    os.getenv("FRONTEND_URL", "https://localhost:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q4: 如何设置自定义域名？

1. 在 Render Dashboard 中进入你的 Web Service
2. 点击 **"Settings"** -> **"Custom Domain"**
3. 输入你的域名（如 `api.myapp.com`）
4. 在域名 DNS 管理处添加 CNAME 记录指向 `你的服务名.onrender.com`
5. Render 会自动申请和续期 SSL 证书

### Q5: 免费版有哪些限制？

| 限制项 | 免费版 |
|--------|--------|
| 内存 | 512 MB |
| 带宽 | 限制 |
| 休眠策略 | 15 分钟不活动后休眠 |
| 构建时长 | 每月 500 分钟 |
| 并发连接 | 限制 |
| PostgreSQL | 1 GB 存储 |

---

## 完整的部署检查清单

- [ ] 项目在本地运行正常
- [ ] requirements.txt 已创建
- [ ] Dockerfile 已创建
- [ ] .gitignore 已配置
- [ ] 代码已推送到 GitHub
- [ ] Render 账号已注册
- [ ] Web Service 已创建
- [ ] 环境变量已配置
- [ ] 部署成功，服务可访问
- [ ] CORS 配置正确
- [ ] 自定义域名已配置（可选）

---

## 参考链接

- [Render 官方文档](https://render.com/docs)
- [Render Dashboard](https://dashboard.render.com)
- [FastAPI 部署文档](https://fastapi.tiangolo.com/deployment/)
- [Docker 官方文档](https://docs.docker.com/)

---

> **下一课：**[CORS 生产配置](./day82_cors_prod.py)