# ADR-0006：前端框架
- 状态：已采纳
- 日期：2026-11-22
- 背景：分享类产品的照片和相册链接会被发到 iMessage、WhatsApp、X 等社交平台和聊天软件（以后也可能有微信），需要显示预览图（M5 要求 Open Graph 预览）；公开内容也希望被搜索引擎收录。社交平台和多数搜索爬虫只读取服务器返回的 HTML，不执行 JavaScript。界面库 React + TypeScript (strict) 已定。
- 选项：
  - A：React + Vite（SPA）：最简单，部署成静态文件即可，不多一个服务 / 服务器返回的是空壳 HTML，分享预览和 SEO 需要额外补丁（后端识别爬虫单独返回 meta 标签）；手机首屏要等 JS 下载后才有内容
  - B：Next.js：服务端渲染，返回已填好 meta 标签和内容的 HTML，分享预览和 SEO 天然支持，首屏快；React 生态中使用最广的框架 / 多一个 Node 服务要部署和监控；概念更多（服务器端 vs 浏览器端代码）；部分功能偏向 Vercel 平台
  - C：React Router 框架模式（原 Remix）：同样支持服务端渲染，更贴近 Web 标准 / 使用者明显少于 Next.js
- 决定：B（Next.js，App Router，TypeScript strict）。
- 理由：
  1. 链接分享是产品的核心动作，服务端渲染让分享预览从一开始就正确，不需要补丁。
  2. 公开相册可以被搜索引擎收录。
  3. 符合选型原则：React 生态中最主流的选择，开源免费。
- 代价：
  - 多一个 Node 服务要部署和监控（托管见 ADR-0007）。
  - 概念比 SPA 多；代码中要清楚标明哪些在服务器运行、哪些在浏览器运行。
- 版本核实（2026-11-22，npm registry）：next 16.4.6、react 19.3.1、vite 8.3.8、react-router 8.5.2。具体版本在 M0 前端骨架时锁定。
- 以后什么情况下重新评估：Next.js 的维护状况或许可发生不利变化；服务端渲染的运维成本明显超过收益时，写新 ADR。

## 约定（为了以后能换、能扩展）
1. **业务逻辑和权限判断全部在 FastAPI 后端。** Next.js 只负责渲染页面和调用后端 API，不直接连数据库、Redis 或对象存储。以后换前端框架或增加原生 App，后端不需要改。
2. **前端调用后端统一使用从 OpenAPI 生成的 TS client**（`docs/architecture.md` 第 1 节已定），不手写请求类型。
3. **用 Docker 自己托管 Next.js（`output: "standalone"`），不使用 Vercel 专有功能**，部署平台可以自由更换。
4. **不依赖 Next.js middleware 做鉴权**；页面需要的权限判断都由后端 API 返回。锁定 Next.js 版本，依赖扫描报警后及时升级。

