# ADR-0008：事务邮件服务
- 状态：已采纳
- 日期：2026-11-22
- 背景：邮箱验证和找回密码（M1），以及以后的通知，需要可靠的事务邮件服务，邮件不能进垃圾箱。自己的服务器直接发信几乎一定被判为垃圾邮件，所以要使用有发信信誉的服务商，并在域名上配置 SPF、DKIM、DMARC。
- 选项（价格 2026-11-22 官网核实）：
  - A：Resend：免费 3,000 封/月、100 封/天；Pro $20/月 5 万封；接入简单，支持 HTTP API 和 SMTP / 公司较新，规模不如老牌服务；官网未说明免费档是否永久
  - B：Postmark：送达率口碑好，区分事务和营销邮件流 / 免费仅 100 封/月；Basic $15/月 1 万封
  - C：AWS SES：行业最主流之一，$0.10/千封，量大时最便宜，支持 SMTP / 无免费额度（新 AWS 账号赠额可抵扣）；新账号在沙箱中（只能发给已验证地址、200 封/24 小时），需申请正式使用（AWS 承诺 96 小时内首次回复）；配置繁琐
  - D：SendGrid：老牌、使用广 / 2025 年取消永久免费档，仅 60 天试用；Essentials $19.95/月起
  - 另看过：Mailgun（免费 100 封/天）、Brevo（免费 300 封/天）
- 决定：分阶段。Beta 期使用 A（Resend 免费档）；超过升级阈值后迁移到 C（AWS SES）。
- 理由：
  1. 按选型原则：最主流的是 SES / SendGrid，但 SendGrid 不再免费，SES 配置重且有沙箱；Beta 期邮件量很小，Resend 免费档足够，费用 $0。
  2. 量大后 SES 最主流且最便宜（5 万封约 $5，Resend 为 $20）。
- 代价：
  - Resend 免费档每天最多 100 封，注册高峰日部分邮件会延后。
  - 迁移到 SES 时需要申请脱离沙箱、配置退信 / 投诉通知。

## 升级触发条件（Claude 提出、Logan 于 2026-11-22 同意；属于运营参数，调整时由 Logan 确认即可，不需要新 ADR）
满足任意一条就评估迁移到 SES：每月超过 3,000 封；经常触及每天 100 封上限；Resend 免费档条款变化；送达率出现问题。

## 约定（可替换性与安全）
1. 所有发信集中在一个模块（如 `core/email.py`），业务代码只调用"发送某类邮件给某人"，不直接调用服务商 SDK；服务商、密钥、发件地址来自配置。
2. 发信通过 Celery 后台任务执行，失败自动重试，不阻塞接口。
3. 发件地址使用我们自己的域名（如 `no-reply@<域名>`），在 Cloudflare DNS 中配置 SPF、DKIM、DMARC；换服务商只需新增 DNS 记录。
4. 开发和测试环境不发真实邮件，使用本地邮件捕获工具（具体工具在 M1 方案中按 ADR 流程确定）。
5. M1 安全要求：找回密码、重发验证邮件除了按 IP 和邮箱限流，还要有全局每日发信上限和告警（防止有人耗尽每天 100 封的额度）；重置链接短时效、一次性。
6. DMARC 先用 `p=none` 加报告地址，确认 SPF/DKIM 对齐后再收紧为 `quarantine` / `reject`。

## 来源
- https://resend.com/pricing
- https://postmarkapp.com/pricing
- https://aws.amazon.com/ses/pricing/ 、https://docs.aws.amazon.com/console/ses/sandbox
- https://www.twilio.com/en-us/products/email-api/pricing 、https://www.twilio.com/en-us/changelog/sendgrid-free-plan
- https://www.mailgun.com/pricing/ 、https://www.brevo.com/pricing/
