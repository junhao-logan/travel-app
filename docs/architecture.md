# 架构与技术栈

> 【已定】= 已确认；【建议】= 需要对应 ADR 被采纳后才算数。

## 1. 技术栈
| 层 | 选择 | 状态 |
|---|---|---|
| 后端 | Python 3.12 + FastAPI | 【已定】 |
| 数据库 | PostgreSQL 16 + SQLAlchemy 2.0 + Alembic | 【已定】 |
| 缓存 / 队列中间件 | Redis | 【已定】 |
| 对象存储 | 本地 MinIO；线上 Cloudflare R2；统一用 boto3（S3 标准 API）访问（ADR-0005） | 【已定】 |
| 异步任务 | Celery（ADR-0003） | 【已定】 |
| 认证 | 服务端 session（Redis）+ httpOnly cookie（ADR-0004） | 【已定】 |
| 前端 | Next.js + React + TypeScript (strict)，自托管，只负责渲染（ADR-0006） | 【已定】 |
| 前后端类型对齐 | 根据 FastAPI 的 OpenAPI 自动生成 TS client | 【已定】 |
| 开发环境 | WSL + Docker Compose | 【已定】 |
| 事务邮件 | Beta 期 Resend 免费档 → 量大后 AWS SES，统一经 `core/email.py` 发送（ADR-0008） | 【已定】 |
| 部署 | 分阶段：Beta 单台 VPS + Docker Compose + Caddy（反向代理、自动 HTTPS）→ 成长期 Render → 大规模 AWS（ADR-0007）；镜像仓库在 M4 方案中确定 | 【已定】 |
| 代码质量 | ruff、mypy (strict)、pytest；ESLint、Prettier；pre-commit | 【已定】 |
| CI | GitHub Actions（lint + 类型检查 + 测试 + 依赖扫描） | 【已定】 |

## 2. 后端分层（必须遵守）
```
api/           → 只负责：解析请求、调用 service、返回响应。不写业务逻辑，不碰数据库。
services/      → 业务逻辑和权限判断。
repositories/  → 唯一可以执行数据库查询的地方。
models/        → SQLAlchemy ORM 模型。
schemas/       → Pydantic 请求/响应模型（不直接返回 ORM 对象）。
core/          → 配置、日志、安全、异常、依赖注入；对象存储封装（storage.py，ADR-0005）、邮件封装（email.py，ADR-0008）。
workers/       → 异步任务。
```

## 3. 核心流程：照片上传
1. 前端请求 `POST /uploads`，带上文件类型和大小。
2. 后端校验（类型白名单、大小上限、登录状态、用户配额），创建 `status=pending` 的照片记录，返回短时效的 **presigned PUT URL**。
3. 前端拿这个 URL 直接把文件传到对象存储（文件不经过后端）。
4. 前端调用 `POST /photos/{id}/complete`。
5. 后端把任务放进队列，worker 负责：
   - 用文件头（magic bytes）校验确实是图片
   - HEIC 转码
   - 清掉 EXIF（尤其是 GPS）
   - 原图尺寸超过上限的缩小；生成缩略图和 WebP
   - 把状态改成 `ready`；失败则改成 `failed`
6. 只有 `ready` 的照片会对外展示。定时任务清理长期处于 `pending` 的记录和残留文件。

## 4. 存储原则
- 数据库只存元数据：对象存储的 key、尺寸、状态、所属用户。不存图片本体。
- bucket 私有，对外访问走 CDN 或带签名的 URL。未处理的原图和私有照片只能用签名 URL 访问，只有公开且 ready 的衍生图可以走公开 CDN（见 ADR-0005 访问控制约定）。
- 数据库备份放在单独的私有 bucket（见 ADR-0007）。
- 对象 key 用随机 UUID，不用用户上传的文件名。

## 5. 安全
见 `docs/security-checklist.md`。

## 6. 上线运营要求
- **备份**：数据库每日自动备份，至少实际演练一次恢复；对象存储开启版本控制或设置删除保护期。
- **监控**：错误追踪（如 Sentry）、可用性监控、关键指标（上传成功率、处理耗时）。
- **成本控制**：单用户存储配额和上传频率限制；云服务费用告警；原图尺寸设上限。
- **内容治理**：举报、管理员下架内容、封禁违规账号。
- **法律页面**：服务条款、隐私政策、版权投诉（DMCA）联系方式。
- **用户数据权利**：删除账号时连带删除所有数据（包括对象存储中的文件）；可以导出自己的数据。
- **邮件**：邮箱验证、找回密码（见 ADR-0008）。

## 7. 统一约定
- 错误响应格式：`{"error": {"code": "PHOTO_NOT_FOUND", "message": "..."}}`
- 分页：cursor 分页（`?cursor=...&limit=20`，limit 上限 50）
- 时间：数据库统一存 UTC（`timestamptz`）
- ID：对外暴露 UUID，不暴露自增 ID
- 日志：结构化 JSON，每个请求带 request_id
- 配置：pydantic-settings 从环境变量读取；`.env.example` 列出所有变量
  - 只列代码实际读取的变量；新功能需要新变量时，在同一个 PR 里加进 `.env.example`，不提前列"以后可能用到"的变量
  - 变量名用行业标准名、不加前缀（如 `DATABASE_URL`、`REDIS_URL`），托管平台注入时不用改名（ADR-0007）
  - `.env.example` 里只放本地开发用的占位密码；生产环境的密码和密钥另外生成，只存在服务器上
  - 品牌名只出现在 `SITE_NAME`（ADR-0009）

## 8. 目录结构
单仓库（monorepo）：前后端在同一个仓库，一个 PR 可以同时改接口和页面。代码中统一使用内部代号 `travelapp`（ADR-0009）。

```
travel-app/
├── backend/               FastAPI + Celery worker：同一份代码、同一个镜像、两种启动命令
│   ├── src/travelapp/     Python 包（src 布局：测试 import 的是安装后的包，和镜像里的代码一致）
│   │   └── api/ services/ repositories/ models/ schemas/ core/ workers/   （分层见第 2 节）
│   ├── tests/
│   └── migrations/        Alembic
├── frontend/              Next.js（ADR-0006）
├── infra/                 生产部署配置：Caddyfile、生产 compose 等（ADR-0007）
├── scripts/               开发脚本，如根据 OpenAPI 生成 TS client
├── docs/
├── compose.yaml           本地开发：一条命令启动全部服务
├── .env.example
└── README.md
```

各部分由 roadmap 中哪一项创建：
| 路径 | 创建于 |
|---|---|
| `backend/`、`frontend/`（占位说明）、`.env.example`、README 启动说明 | M0 目录结构 |
| `compose.yaml` | M0 Docker Compose |
| `backend/src/travelapp/` 分层目录、`backend/tests/` | M0 后端骨架 |
| `backend/migrations/` | M0 Alembic 初始化 |
| `frontend/` 内的 Next.js 项目 | M0 前端骨架 |
| `scripts/` | M0 生成 TS client 的脚本 |
| `infra/` | M4 部署上线 |

目录在需要它的那一项里才创建，不提前建空目录。
