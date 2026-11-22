# ADR-0003：异步任务框架
- 状态：已采纳
- 日期：2026-11-22
- 背景：ADR-0002 需要一个基于 Redis 的任务框架来运行图片处理（magic bytes 校验、HEIC 转码、清除 EXIF、缩略图）和定时清理任务（长期 pending 的记录和残留文件）。
- 选项：
  - A：Celery：最成熟、使用最广，自带重试、`acks_late`（worker 崩溃不丢任务）、定时任务（Celery Beat）；默认多进程，适合 CPU 密集任务 / 配置较重、概念多，不是原生 asyncio
  - B：ARQ：轻量、原生 asyncio，和 FastAPI 风格一致 / 官方 README 标注"In maintenance only mode"（见 python-arq/arq#510），不再开发
  - C：Dramatiq：比 Celery 简单，可靠性设计好 / 社区较小，定时任务需要额外插件
  - D：Taskiq：原生 asyncio / 仍是 0.x，API 可能变化；asyncio 对 CPU 密集任务没有帮助
- 决定：A（Celery），broker 使用已定的 Redis。
- 理由：
  1. worker 的主要工作是 CPU 密集的图片处理，asyncio 不带来收益，Celery 的多进程模型更合适。
  2. 重试、任务确认、定时任务都是现成功能，不需要自己实现。
  3. 行业内使用最广，后续开发者和 Claude 都熟悉，问题容易查到答案。
  4. B 已进入只维护状态，不适合长期运营的产品。
- 代价：
  - 配置较重：M0 中把 Celery 配置集中在一个模块里并写注释。
  - 不是原生 async：如果 API 使用异步 SQLAlchemy，worker 需要用同步 session 或在任务中用 `asyncio.run()` 复用 repository，具体做法在 M0 后端骨架方案中确定。
  - 定时任务需要额外运行 Celery Beat 进程。
- 核实记录（2026-11-22）：Celery 5.7.0 于 2026-11-05 发布（https://pypi.org/project/celery/）；ARQ 0.28.0 于 2026-04-16 发布，README 标注只维护（https://github.com/python-arq/arq）；Dramatiq 2.2.1、Taskiq 0.13.0（PyPI）。
- 以后什么情况下重新评估：任务量大到需要复杂路由或多语言 worker，或 Celery 停止维护时，写新 ADR。
