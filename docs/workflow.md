# 工作流程

> CLAUDE.md 里是精简版规则，这里是完整说明。规则冲突时以 CLAUDE.md 为准。

## 谁做什么
| 角色 | 负责 |
|---|---|
| Logan | 定方向、确认方案和 ADR、读 diff、合并 PR |
| Claude Code | 出方案、写代码和测试、跑检查、更新文档、开 PR |
| CI（GitHub Actions） | 每个 PR 自动跑 lint、类型检查、测试；不通过就不能合并 |
| Hooks | 自动执行的规则：会话开始时显示进度、编辑后自动格式化、禁止在 main 上提交（**只在本地 Claude Code 生效**） |
| GitHub 分支保护 | main 必须走 PR、CI 通过才能合并（本地和云端都生效，最后一道关） |

## 两种工作环境
| | Claude Code Projects（云端线程） | 本地 Claude Code |
|---|---|---|
| 自动加载 | `CLAUDE.md`、`.claude/rules/` | 全部：`CLAUDE.md`、rules、skills、agents、hooks、权限 |
| 不加载 | skills、agents、hooks、`.claude/settings.json` | — |
| 怎么触发流程 | 直接用自然语言说"做 M1 注册功能"，rules 会自动生效 | `/feature`、`/adr`、`/wrap-up` |
| 强制保障 | 分支保护 + CI + Project 指令 | hooks + 权限 + 分支保护 + CI |

所有流程的正文都写在 `.claude/rules/` 里，两边读的是同一份。skills 和 agents 只是本地的快捷入口。

## 一次会话（本地）
1. 在仓库目录运行 `claude`。SessionStart hook 会自动显示 roadmap 的"当前位置"。
2. Claude 用一句话确认当前位置和下一步。
3. 做一个功能：`/feature <功能名>`。
4. 结束：`/wrap-up`。
5. 下一个功能：先 `/clear` 清空上下文，再开始。不要在一个超长会话里连做多个功能。

## 在 Projects 里
- 在项目对话里说要做什么，Claude（协调者）会为每个任务开一个线程，每个线程一个分支、一个 PR。
- Project 指令里已要求：一次只开一个线程；方案先发出来等确认；不合并。
- 线程开了 PR 后会自动盯着 CI，CI 失败会自己修。
- Logan 在 Overview 里看哪些线程在等他、哪些 PR 待审，审完后自己在 GitHub 上合并。

## 流程正文
- 新功能：`.claude/rules/feature-workflow.md`
- ADR：`.claude/rules/adr-workflow.md`
- 审查：`.claude/rules/review.md`
- 收尾：`.claude/rules/wrap-up.md`

流程只在这些文件里写一份，其他地方只引用，避免出现两个版本。
