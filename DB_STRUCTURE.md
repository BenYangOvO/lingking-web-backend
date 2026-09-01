# 数据库结构（SQLite，data/lingking.db）

> 由 lingking-web-backend 后端自动创建（`db.py` 中的 `init_db()`，幂等）。

## users 表（用户）

| 字段           | 类型     | 约束                | 说明                        |
|----------------|----------|---------------------|-----------------------------|
| id             | INTEGER  | PRIMARY KEY AUTOINCREMENT | 用户 ID             |
| username       | TEXT     | NOT NULL, UNIQUE    | 用户名（2-20 位字母/数字/下划线/中文） |
| email          | TEXT     | NOT NULL, UNIQUE    | 邮箱（登录也支持邮箱）        |
| password_hash  | TEXT     | NOT NULL            | PBKDF2-SHA256 哈希，格式 `pbkdf2_sha256$迭代次数$盐$摘要` |
| nickname       | TEXT     | NOT NULL DEFAULT '' | 昵称                        |
| avatar         | TEXT     | NOT NULL DEFAULT '' | 头像 URL                    |
| birthday       | TEXT     | NOT NULL DEFAULT '' | 生日 (YYYY-MM-DD)           |
| bio            | TEXT     | NOT NULL DEFAULT '' | 个人简介                    |
| role           | TEXT     | NOT NULL DEFAULT 'member' | 角色（admin/member）  |
| created_at     | INTEGER  | NOT NULL            | 注册时间（unix 秒）         |

索引：`idx_users_username`、`idx_users_email`

## submissions 表（投稿 / 帖子）

| 字段           | 类型     | 约束                | 说明                        |
|----------------|----------|---------------------|-----------------------------|
| id             | INTEGER  | PRIMARY KEY AUTOINCREMENT | 投稿自增 ID         |
| uuid           | TEXT     | UNIQUE              | 全局唯一标识符（32位UUID小写十六进制字符串，供前端路由与SEO爬虫使用） |
| board          | TEXT     | NOT NULL            | 板块：photo / resource / diary |
| status         | TEXT     | NOT NULL DEFAULT 'pending' | 状态：pending / approved / rejected |
| payload        | TEXT     | NOT NULL            | 投稿详情 JSON 文本          |
| submitter_id   | INTEGER  | NOT NULL            | 提交人用户 ID               |
| submitter_name | TEXT     | NOT NULL DEFAULT '' | 提交人展示名称              |
| created_at     | INTEGER  | NOT NULL            | 创建时间（unix 秒）         |
| reviewed_at    | INTEGER  | NULL                | 审核时间（unix 秒）         |
| reviewed_by    | INTEGER  | NULL                | 审核管理员 ID               |
| review_note    | TEXT     | NULL                | 审核意见（JSON 文本）       |

索引：`idx_sub_uuid` (UNIQUE)、`idx_sub_board`、`idx_sub_status`、`idx_sub_created`、`idx_sub_submitter`

## hidden_static 表（隐藏静态内容）

| 字段           | 类型     | 约束                | 说明                        |
|----------------|----------|---------------------|-----------------------------|
| id             | INTEGER  | PRIMARY KEY AUTOINCREMENT | 记录自增 ID         |
| board          | TEXT     | NOT NULL            | 板块：photo / resource / diary |
| static_id      | INTEGER  | NOT NULL            | 静态数据项 ID               |
| hidden_at      | INTEGER  | NOT NULL            | 隐藏时间（unix 秒）         |

约束：`UNIQUE(board, static_id)`

## site_content 表（站点固定内容）

| 字段           | 类型     | 约束                | 说明                        |
|----------------|----------|---------------------|-----------------------------|
| id             | INTEGER  | PRIMARY KEY AUTOINCREMENT | 记录自增 ID         |
| slug           | TEXT     | NOT NULL, UNIQUE    | 页面标识（home/about/history/departments/studio） |
| content_json   | TEXT     | NOT NULL            | 页面内容 JSON 文本          |
| updated_at     | INTEGER  | NOT NULL            | 更新时间（unix 秒）         |
| updated_by     | INTEGER  | NULL                | 更新管理员 ID               |

索引：`idx_site_content_slug`

## 变更记录

- 2024-08-26：新增 users 表（最简登录系统）
- 2026-08-30：新增 submissions、hidden_static、site_content 表
- 2026-09-01：submissions 表新增 `uuid` 唯一标识符字段及 `idx_sub_uuid` 唯一索引，支持已有数据自动回填与 SEO Path 路由