# 纯 Python 标准库实现，无需安装任何第三方依赖

本目录是「凌镜摄影社团」社员博客的**后端 API 服务**（当前仅含最简用户登录系统）。

## 快速启动

```bash
python3 app.py
```

- 默认监听 `0.0.0.0:8000`，可用环境变量 `PORT`、`HOST` 覆盖
- 数据保存在 `data/lingking.db`（SQLite，自动建表）
- token 签名密钥自动生成并落盘 `data/.secret`，也可用环境变量 `LINGKING_TOKEN_SECRET` 指定

## API

| 方法 | 路径              | 说明                                             |
|------|-------------------|--------------------------------------------------|
| GET  | `/api/health`     | 健康检查                                         |
| POST | `/api/auth/register` | 注册 `{username, email, password}`，成功返回 `{token, user}` |
| POST | `/api/auth/login` | 登录 `{identifier, password}`（identifier 为用户名或邮箱），成功返回 `{token, user}` |
| GET  | `/api/auth/me`    | 需 `Authorization: Bearer <token>`，返回当前用户  |

## 安全说明

- 密码使用 PBKDF2-HMAC-SHA256（20 万次迭代 + 随机盐）哈希存储，不存明文
- token 为 HMAC-SHA256 签名，有效期 7 天，无状态（服务端不存会话）
- 对外接口永不返回 `password_hash` 字段