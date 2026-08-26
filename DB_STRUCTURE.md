# 数据库结构（SQLite，data/lingking.db）

> 由 lingking-web-backend 后端自动创建（`db.py` 中的 `init_db()`，幂等）。

## users 表

| 字段           | 类型     | 约束                | 说明                        |
|----------------|----------|---------------------|-----------------------------|
| id             | INTEGER  | PRIMARY KEY AUTOINCREMENT | 用户 ID             |
| username       | TEXT     | NOT NULL, UNIQUE    | 用户名（2-20 位字母/数字/下划线/中文） |
| email          | TEXT     | NOT NULL, UNIQUE    | 邮箱（登录也支持邮箱）        |
| password_hash  | TEXT     | NOT NULL            | PBKDF2-SHA256 哈希，格式 `pbkdf2_sha256$迭代次数$盐$摘要` |
| nickname       | TEXT     | NOT NULL DEFAULT '' | 昵称（预留）                |
| avatar         | TEXT     | NOT NULL DEFAULT '' | 头像 URL（预留）            |
| role           | TEXT     | NOT NULL DEFAULT 'member' | 角色（预留：admin/member） |
| created_at     | INTEGER  | NOT NULL            | 注册时间（unix 秒）         |

索引：`idx_users_username`、`idx_users_email`

## 变更记录

- 2024-08-26：新增 users 表（最简登录系统）