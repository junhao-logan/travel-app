# CLAUDE.md

旅游照片分享平台：一个要真正上线运营的产品（同时会写进简历）。做决定以"对产品好"为准。
负责人：Logan。主要由你（Claude）编写代码；Logan 审方案、读 diff、做决定，并且要能解释每个设计。

## 每次会话 / 每个线程必须遵守
1. **开始时**：读 `docs/roadmap.md` 的"当前位置"，用一句话告诉 Logan 现在在哪个里程碑、下一步是什么。
2. **做功能**：一律按 `.claude/rules/feature-workflow.md` 执行。先出方案，Logan 确认后才能写代码。
3. **技术决策**：按 `.claude/rules/adr-workflow.md` 执行。
4. **结束时**：按 `.claude/rules/wrap-up.md` 收尾。
5. 不确定的事就问，不要自己猜。缺少需要的东西（仓库、密钥、服务）时，说明缺什么然后停下，不要模拟或绕过。

## 硬性规则
- 一次只做一个功能；不跳里程碑；不加需求外的功能。有建议就提出来，由 Logan 决定。
- 不在 `main` 上直接提交。一个功能一个分支、一个 draft PR。**不合并 PR、不 force push、不修改 CI 配置**，除非 Logan 明确要求。
- 引入新技术或新依赖前先写 ADR，Logan 确认后才能安装。
- 区分"已定"和"建议"，不要把你的建议写成 Logan 的决定。
- 没有测试的功能 = 没完成。lint、类型检查、测试必须全部通过。
- 每个功能完成前按 `.claude/rules/review.md` 做安全审查和代码审查。
- 不读、不改、不输出 `.env` 及任何密钥。
- 每个方案都要说明理由和替代选项（Logan 需要能讲清楚）。

## 文档（单一事实来源，改了就跟代码在同一个 commit 里提交）
- `docs/charter.md`：范围、阶段、不做的事、产品质量标准
- `docs/architecture.md`：技术栈、分层、上传流程、运营要求、统一约定
- `docs/security-checklist.md`：每个功能都要过的安全清单
- `docs/roadmap.md`：里程碑、验收标准、当前位置、完成记录
- `docs/decisions/`：ADR，每条决策一个文件
- `docs/workflow.md`：完整工作流程说明

## 后端分层（必须遵守）
`api/`（只做请求解析和响应）→ `services/`（业务逻辑和权限）→ `repositories/`（唯一能查数据库的地方）。
`schemas/` 放 Pydantic 模型，不直接返回 ORM 对象。新模块以 M1 的 users 模块为样板。

## 约定
- 代码、注释、commit 信息、PR 描述用英文；和 Logan 讨论用中文。
- commit 用 Conventional Commits（`feat:`、`fix:`、`chore:`、`docs:`、`test:`、`refactor:`）。
- 分支命名：`feat/<milestone>-<short-name>`，例如 `feat/m1-register`。
- 错误格式、分页、时间、ID 等约定见 `docs/architecture.md` 第 7 节。

## 常用命令
（在 M0 搭好后补上：启动、测试、lint、类型检查、迁移、生成前端 client）
