# ADR-0007：部署平台
- 状态：已采纳
- 日期：2026-11-22
- 背景：需要运行 API（FastAPI）、worker + beat（Celery）、前端（Next.js），以及 PostgreSQL 和 Redis；一个人运维，要求省心、可预测的费用、自动部署。目标用户在海外（`docs/charter.md` 2.1）。Logan 要求：Beta 期花费极小，用户和收入增长后再升级。
- 照片在对象存储（ADR-0005，R2），域名和 CDN 在 Cloudflare，都与服务器无关；换托管平台时只迁移程序和数据库。
- 选项：
  - A：单台 VPS（如 Hetzner）+ Docker Compose：最便宜（约 €7–8/月含整机备份），和开发环境一致 / 备份、安全更新、宕机处理要自己做；单点故障
  - B：PaaS（Render；同类还有 Railway、Fly.io）：自动部署、托管数据库（带时间点恢复）、几乎不用运维、价格固定 / 比 VPS 贵（本项目精简配置约 $37/月，正常配置 $44–51/月）
  - C：AWS（ECS Fargate + RDS + ElastiCache）：行业最主流、扩展性最强 / 配置复杂、账单项目多，估算 $75–90/月起，对当前规模过剩
  - D：Oracle Cloud 永久免费实例：$0 / 闲置实例可能被回收、账号风控，不适合存放真实用户数据
- 决定：分阶段。
  | 阶段 | 平台 | 预计费用 |
  |---|---|---|
  | 开发（M0–M3） | 本地 Docker Compose | $0 |
  | Beta（M4 上线、M5 内测、小规模公开测试） | A：单台 VPS（2 vCPU / 4GB）+ Docker Compose + Caddy（自动 HTTPS） | 约 $8/月 |
  | 成长期 | B：Render | $50–100/月 |
  | 大规模 | C：AWS（届时写新 ADR） | 视规模 |
- 理由：
  1. Logan 要求 Beta 期花费极小；VPS 是可靠选项中最便宜的，且和开发环境完全一致，最容易理解。
  2. 按选型原则：最主流的是 AWS，但贵且复杂；先用低价方案，并通过下方约定保证可以平滑迁移到 Render 或 AWS。
- 代价：
  - Beta 期只有一台服务器，故障时会停机（分钟到小时级）。
  - 数据库备份、安全更新、部署脚本要自己写好并测试。
  - Hetzner 官网在 2026-11-22 核实时各套餐显示"暂时缺货"；M4 时如仍缺货，换同类 VPS（DigitalOcean、Vultr 等，约 $12–24/月），本 ADR 不绑定具体服务商。

## Beta 期（VPS）必须做到
1. 数据库每天自动 `pg_dump` 并上传到 R2（保留至少 7 天），外加服务商的整机备份。
2. M4 中至少完成一次从备份恢复的演练（roadmap M4 验收标准）。
3. 开启自动安全更新；只开放 80/443 和 SSH（SSH 只允许密钥登录）。
4. 部署：CI 通过后由 GitHub Actions 通过 SSH 拉取新镜像并重启。
5. 可用性监控和错误追踪按 M4 计划配置（免费档）。
6. 写一份运维手册（启动、部署、备份、恢复、换服务器步骤）。

## 升级触发条件（建议值，可调整；满足任意一条就评估升级到下一阶段）
1. 服务器 CPU 或内存连续一周超过 70%。
2. 一个月内出现 2 次以上需要人工处理的宕机。
3. 月收入能覆盖下一阶段的费用。
4. 每月运维耗时超过几个小时。

## 为了随时能迁移必须遵守的约定
1. 所有服务都是标准 Docker 镜像，配置全部来自环境变量；同一个镜像在 VPS、Render、AWS 上都能运行。
2. 只使用标准 PostgreSQL 和 Redis 功能；迁移 = 导出 → 导入。
3. 平台相关配置只放在独立文件中（如 `compose.prod.yml`、`render.yaml`），不进入业务代码。
4. 域名 DNS 托管在 Cloudflare；迁移的最后一步是修改 DNS 指向。

## 价格核实（2026-11-22，官网）
- Render（https://render.com/pricing 、https://render.com/docs/postgresql-backups 、https://render.com/docs/free）：最小常驻实例 $7/月（512MB）；Postgres 最低 $6/月 + $0.30/GB，时间点恢复 Hobby 3 天 / Pro（$25/月）7 天；Key Value（Redis 兼容）付费 $10/月起；免费 Postgres 30 天后过期，免费服务闲置 15 分钟休眠。
- Railway（https://railway.com/pricing）：Hobby $5/月起按用量计费（约 $10/GB 内存·月、$20/vCPU·月），本项目估算 $25–40/月，账单不固定。
- Fly.io（https://fly.io/docs/about/pricing/）：新组织无免费档；托管 Postgres Basic $38/月起。
- AWS（https://aws.amazon.com/fargate/pricing/）：最小 Fargate 任务约 $9/月；RDS、ElastiCache、负载均衡器价格表未能显示，总价为估算。2025-07-15 后的新账号获赠 $100–200 额度，取代旧的 12 个月免费。
- Hetzner（https://www.hetzner.com/cloud）：CX23（2 vCPU / 4GB / 40GB / 20TB 流量）€5.99/月，备份约 €1.10/月起；当日显示缺货。
- M4 部署前重新核实价格和可用性。
