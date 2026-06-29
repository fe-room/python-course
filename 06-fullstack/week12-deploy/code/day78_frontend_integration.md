# 前端集成指南 — FastAPI 后端对接

> 本文档面向 React / Vue 前端开发者，说明如何调用 FastAPI 后端 API。
> 涵盖 Axios 配置、Token 存储、认证拦截器等核心内容。

---

## 目录

1. [环境准备](#1-环境准备)
2. [Axios 实例配置](#2-axios-实例配置)
3. [用户注册与登录](#3-用户注册与登录)
4. [Token 存储](#4-token-存储)
5. [认证拦截器](#5-认证拦截器)
6. [401 自动刷新处理](#6-401-自动刷新处理)
7. [调用受保护的 API](#7-调用受保护的-api)
8. [完整示例代码](#8-完整示例代码)

---

## 1. 环境准备

### 安装依赖

```bash
# 使用 npm 或 yarn 安装 Axios
npm install axios
# 或
yarn add axios
```

### 后端 API 基础信息

| 项目 | 值 |
|------|-----|
| 后端地址（开发） | `http://localhost:8000` |
| 后端地址（生产） | `https://your-app.onrender.com` |
| API 文档（Swagger） | `http://localhost:8000/docs` |

---

## 2. Axios 实例配置

创建一个 `api.js` 或 `api.ts` 文件，集中管理 Axios 配置。

```javascript
// src/api.js — Axios 实例配置

import axios from 'axios';

// 根据环境变量设置不同的 baseURL
const API_BASE_URL = process.env.REACT_APP_API_URL
  || process.env.VITE_API_URL
  || 'http://localhost:8000';

// 创建 Axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,               // 请求超时时间（10 秒）
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
```

### Vue 3 + Vite 环境变量配置

在项目根目录创建 `.env` 文件：

```env
# .env.development（开发环境）
VITE_API_URL=http://localhost:8000

# .env.production（生产环境）
VITE_API_URL=https://your-app.onrender.com
```

---

## 3. 用户注册与登录

### 注册接口

```javascript
// src/services/auth.js

import api from '../api';

/**
 * 用户注册
 * POST /register
 *
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @param {string} email    - 邮箱
 * @returns {Promise} 注册结果
 */
export async function register(username, password, email) {
  const response = await api.post('/register', {
    username,
    password,
    email,
  });
  return response.data;
}
```

### 登录接口

```javascript
/**
 * 用户登录
 * POST /token
 *
 * 注意：FastAPI 的 OAuth2PasswordRequestForm 要求
 * 使用 application/x-www-form-urlencoded 格式提交数据，
 * 因此需要使用 URLSearchParams 转换数据。
 *
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {Promise} 包含 access_token 和 refresh_token 的响应
 */
export async function login(username, password) {
  // FastAPI 的 OAuth2PasswordRequestForm 需要表单格式
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await api.post('/token', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  // 登录成功后保存 Token
  const { access_token, refresh_token } = response.data;
  saveTokens(access_token, refresh_token);

  return response.data;
}
```

---

## 4. Token 存储

### 安全的 Token 存储策略

```javascript
// src/utils/tokenStorage.js

/**
 * Token 存储工具
 *
 * 存储位置选择：
 *   - localStorage  : 简单易用，但存在 XSS 攻击风险
 *   - httpOnly Cookie: 更安全，但实现更复杂
 *
 * 本教程使用 localStorage 以便演示，
 * 生产环境建议使用 httpOnly Cookie 或
 * 结合后端配置的安全策略。
 */

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

/**
 * 保存 Token 到 localStorage
 */
export function saveTokens(accessToken, refreshToken) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
}

/**
 * 获取 access_token
 */
export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * 获取 refresh_token
 */
export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * 清除所有 Token（登出时调用）
 */
export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * 检查是否已登录
 */
export function isAuthenticated() {
  return !!getAccessToken();
}
```

---

## 5. 认证拦截器

拦截器（Interceptor）可以在每次请求发送前自动添加 `Authorization` 头。

```javascript
// src/api.js — 完整配置（含拦截器）

import axios from 'axios';
import { getAccessToken, clearTokens } from './utils/tokenStorage';

const API_BASE_URL = process.env.REACT_APP_API_URL
  || process.env.VITE_API_URL
  || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==========================================
// 请求拦截器（Request Interceptor）
// ==========================================
// 在每次请求发送之前执行，
// 自动在请求头中添加 Bearer Token。
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      // 设置 Authorization 头
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // 请求配置出错时的处理
    return Promise.reject(error);
  }
);

// ==========================================
// 响应拦截器（Response Interceptor）
// ==========================================
// 在每次收到响应后执行，
// 统一处理 401 错误（Token 过期）。
api.interceptors.response.use(
  (response) => {
    // 请求成功，直接返回响应
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // 如果是 401 错误且不是刷新 Token 的请求
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // 尝试使用 refresh_token 获取新的 access_token
      const refreshed = await refreshAccessToken(originalRequest);

      if (refreshed) {
        // 刷新成功，重试原始请求
        return api(originalRequest);
      }

      // 刷新失败，清除 Token 并跳转到登录页
      clearTokens();
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

/**
 * 尝试刷新 access_token
 */
async function refreshAccessToken(originalRequest) {
  try {
    const refreshToken = getRefreshToken();
    if (!refreshToken) return false;

    // 调用刷新端点
    const response = await axios.post(`${API_BASE_URL}/refresh`, {
      refresh_token: refreshToken,
    });

    const { access_token, refresh_token } = response.data;

    // 保存新 Token
    saveTokens(access_token, refresh_token);

    // 更新原始请求的 Authorization 头
    originalRequest.headers.Authorization = `Bearer ${access_token}`;

    return true;
  } catch (error) {
    console.error('Token 刷新失败:', error);
    return false;
  }
}

export default api;
```

---

## 6. 401 自动刷新处理流程

```
用户请求受保护资源
        │
        ▼
请求拦截器自动添加 Authorization: Bearer xxx
        │
        ▼
后端验证 Token
        │
    ┌───┴───┐
    │       │
  有效    无效 (401)
    │       │
    │       ▼
    │   响应拦截器捕获 401
    │       │
    │       ▼
    │   检查是否有 refresh_token
    │       │
    │   ┌───┴───┐
    │   │       │
    │  有      无 → 跳转登录页
    │   │
    │   ▼
    │  POST /refresh
    │       │
    │   ┌───┴───┐
    │   │       │
    │  成功    失败 → 跳转登录页
    │   │
    │   ▼
    │  保存新 Token
    │  重试原始请求
    │       │
    │       ▼
    │  请求成功 ✓
```

---

## 7. 调用受保护的 API

### React 示例

```jsx
// src/components/UserProfile.jsx

import React, { useState, useEffect } from 'react';
import api from '../api';

function UserProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // GET /me — 需要有效的 Bearer Token
    api.get('/me')
      .then(response => {
        setUser(response.data);
      })
      .catch(err => {
        setError(err.response?.data?.detail || '获取用户信息失败');
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) return <div>加载中...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div>
      <h2>用户信息</h2>
      <p>用户名: {user.username}</p>
      <p>邮箱: {user.email}</p>
    </div>
  );
}

export default UserProfile;
```

### Vue 3 示例

```vue
<!-- src/components/UserProfile.vue -->

<template>
  <div>
    <div v-if="loading">加载中...</div>
    <div v-else-if="error" style="color: red">{{ error }}</div>
    <div v-else>
      <h2>用户信息</h2>
      <p>用户名: {{ user.username }}</p>
      <p>邮箱: {{ user.email }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

const user = ref(null);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    const response = await api.get('/me');
    user.value = response.data;
  } catch (err) {
    error.value = err.response?.data?.detail || '获取用户信息失败';
  } finally {
    loading.value = false;
  }
});
</script>
```

---

## 8. 完整示例代码

### 项目结构

```
src/
├── api.js                    # Axios 实例 + 拦截器
├── utils/
│   └── tokenStorage.js       # Token 存储工具
├── services/
│   └── auth.js               # 认证相关 API 调用
└── components/
    ├── LoginForm.jsx         # 登录表单
    └── UserProfile.jsx       # 用户信息页面
```

### 完整的登录组件

```jsx
// src/components/LoginForm.jsx

import React, { useState } from 'react';
import { login } from '../services/auth';

function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const result = await login(username, password);
      console.log('登录成功:', result);
      // 跳转到首页
      window.location.href = '/profile';
    } catch (err) {
      const message = err.response?.data?.detail
        || err.message
        || '登录失败，请重试';
      setError(message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>用户登录</h2>

      {error && <div style={{ color: 'red' }}>{error}</div>}

      <div>
        <label>用户名:</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>

      <div>
        <label>密码:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>

      <button type="submit">登录</button>
    </form>
  );
}

export default LoginForm;
```

---

## 常见问题 FAQ

### Q: 为什么 Postman 能调通，浏览器调不通？

A: 通常是 **CORS 问题**。Postman 不执行 CORS 策略，但浏览器会。检查后端是否正确配置了 CORS 中间件。

### Q: 登录后页面刷新就丢失登录状态？

A: 检查 Token 是否正确保存到了 `localStorage`，以及请求拦截器是否能正确读取 Token。

### Q: 如何调试 Token 相关的问题？

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network（网络）** 标签
3. 查看请求头中是否包含 `Authorization: Bearer xxx`
4. 查看响应状态码和错误信息

---

> **下一课：**[Render 部署指南](./day81_render_deploy.md)