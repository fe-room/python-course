# CI/CD 入门与 GitHub Actions 实战

## 一、什么是 CI/CD？

### CI（持续集成）

**Continuous Integration** 指的是开发人员频繁地将代码合并到主干分支，每次合并都通过自动化构建和测试来验证。

核心流程：

```
开发者推送代码 → 自动拉取 → 安装依赖 → 运行测试 → 报告结果
```

### CD（持续交付 / 持续部署）

**Continuous Delivery** — 代码通过测试后自动准备好部署到生产环境，但需要手动确认。
**Continuous Deployment** — 代码通过测试后自动部署到生产环境，无需人工干预。

### 前端工程师熟悉的 CI 工具对比

| 工具 | 类型 | 特点 |
|------|------|------|
| GitHub Actions | 云端 CI/CD | 与 GitHub 深度集成，市场丰富 |
| GitLab CI | 云端 CI/CD | Pipeline as Code，内置注册表 |
| Jenkins | 自托管 CI/CD | 高度可定制，配置复杂 |
| CircleCI | 云端 CI/CD | 速度快，缓存机制强 |
| Travis CI | 云端 CI/CD | 配置简单，生态成熟 |

> 对于前端工程师来说，GitHub Actions 最接近 GitHub Pages + GitHub 生态的使用体验。如果你用过 Vercel 或 Netlify 的自动部署，CI/CD 的核心思想与此相同——**代码变更触发自动化流程**。

---

## 二、GitHub Actions 核心概念

### Workflow（工作流）

一个可配置的自动化流程，定义在 `.github/workflows/` 目录下的 YAML 文件中。

```yaml
name: CI          # 工作流名称
on: [push, pull_request]  # 触发条件
```

### Job（作业）

工作流中的一个任务单元，在同一 runner 中执行。

```yaml
jobs:
  test:           # Job ID
    runs-on: ubuntu-latest
    steps:
      - ...
```

### Step（步骤）

Job 中的单个操作，可以是运行命令或使用 Action。

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4
  - name: Run tests
    run: pytest
```

### Runner（运行器）

执行工作流的服务器。GitHub 提供 ubuntu-latest / windows-latest / macos-latest。

### Action（动作）

可复用的单元，可以从 GitHub Marketplace 安装。

---

## 三、测试工作流：`.github/workflows/test.yml`

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ["3.12"]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests with coverage
        run: |
          pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=80

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov/
```

### 关键配置说明

| 配置项 | 说明 |
|--------|------|
| `on.push.branches` | 仅在推送到 main 时触发 |
| `strategy.matrix` | 矩阵构建，可同时测试多个 Python 版本 |
| `actions/cache` | 缓存 pip 依赖，加速后续运行 |
| `--cov-fail-under=80` | 覆盖率低于 80% 视为失败 |

---

## 四、部署工作流：`.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}

      - name: Deploy to Render
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
```

### 部署流程拆解

1. **检出代码** — 获取最新代码
2. **构建 Docker 镜像** — 使用 Docker Buildx 进行多架构构建
3. **推送镜像** — 推送到 GitHub Container Registry（ghcr.io）
4. **触发部署** — 调用 Render 的 Deploy Hook URL

### Docker Hub 替代方案

如需推送到 Docker Hub，将登录步骤替换为：

```yaml
- name: Log in to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}
```

> Render 的 Deploy Hook 获取方式：Render Dashboard > Your Service > Settings > Deploy Hook。具体使用方式参考 Day 81 内容。

---

## 五、关键概念详解

### 5.1 Secrets（密钥）

用于存储敏感信息（API Key、密码等），在 GitHub 仓库的设置页面配置。

**设置路径**：Settings > Secrets and variables > Actions > New repository secret

**使用方式**：

```yaml
steps:
  - name: Use secret
    run: echo "${{ secrets.MY_SECRET }}"
```

**典型 secrets 清单**：

| Secret 名称 | 用途 |
|-------------|------|
| `DOCKER_USERNAME` | Docker Hub 用户名 |
| `DOCKER_PASSWORD` | Docker Hub 密码或 Access Token |
| `RENDER_DEPLOY_HOOK_URL` | Render 部署钩子 URL |
| `PRODUCTION_ENV` | 生产环境变量文件内容 |

### 5.2 Matrix Builds（矩阵构建）

同时测试多个配置组合：

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
    os: [ubuntu-latest, windows-latest]

    # 排除不需要的组合
    exclude:
      - os: windows-latest
        python-version: "3.12"
```

生成的组合：

| # | os | python-version |
|---|----|----------------|
| 1 | ubuntu-latest | 3.10 |
| 2 | ubuntu-latest | 3.11 |
| 3 | ubuntu-latest | 3.12 |
| 4 | windows-latest | 3.10 |
| 5 | windows-latest | 3.11 |

### 5.3 缓存 pip 依赖

使用 `actions/cache` 可以避免每次运行都重新下载依赖：

```yaml
- name: Cache pip
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

**工作原理**：

- `key` 中的 `hashFiles` 基于 requirements.txt 的内容生成哈希值
- 如果 requirements.txt 未变化，key 匹配，恢复缓存
- 如果 requirements.txt 发生变化，key 不匹配，使用 `restore-keys` 中的部分匹配

---

## 六、Python CI 常见问题及解决方案

### 问题 1：依赖安装缓慢

**解决**：使用缓存 + 仅安装必要依赖

```yaml
- name: Install dependencies
  run: |
    pip install --upgrade pip
    pip install -r requirements.txt
  # 不要安装 dev 依赖
```

### 问题 2：测试找不到模块

**解决**：确保工作目录正确，使用 `python -m pytest` 而非直接 `pytest`

```yaml
- name: Run tests
  run: |
    python -m pytest tests/ -v
```

### 问题 3：数据库相关测试失败

**解决**：使用内存数据库或 CI 提供的服务

```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test_db
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

### 问题 4：覆盖率未生成

**解决**：确保安装 `pytest-cov`，且路径正确

```bash
pip install pytest-cov
pytest --cov=app --cov-report=xml --cov-report=term-missing
```

### 问题 5：Docker 构建失败

**解决**：

- 确保 Dockerfile 在仓库根目录
- 检查 requirements.txt 是否存在
- 使用 `docker build` 本地验证后再推送
- 留意 Docker Hub 的 rate limit

### 问题 6：GitHub Actions 超时

**解决**：

- 默认超时 6 小时，可在 job 级别设置更短超时
- 使用缓存加速依赖安装

```yaml
jobs:
  test:
    timeout-minutes: 30
```

---

## 七、最佳实践总结

| 实践 | 说明 |
|------|------|
| 尽早运行测试 | 在 PR 触发时运行测试，而非合并后 |
| 保持构建快速 | 使用缓存，避免不必要的步骤 |
| 使用矩阵测试 | 确保兼容多个 Python 版本 |
| 保护 main 分支 | 设置分支保护规则，要求 CI 通过才允许合并 |
| 最小化 secrets | 仅暴露必需的密钥 |
| 监控构建状态 | 配置 Slack/Email 通知构建失败 |