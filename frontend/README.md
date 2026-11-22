# frontend

Next.js (App Router) + React + TypeScript strict, self-hosted with Docker
(`output: "standalone"`), see ADR-0006.

The frontend only renders pages and calls the backend API through the TypeScript
client generated from the backend's OpenAPI schema. It never talks to the database,
Redis or object storage directly, and holds no business or permission logic.

> Status: placeholder. Filled in by the M0 roadmap items "前端骨架" (frontend skeleton)
> and "根据 OpenAPI 生成 TS client 的脚本" (client generation script).
> See [`docs/roadmap.md`](../docs/roadmap.md).
