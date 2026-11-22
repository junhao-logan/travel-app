# travel-app

A travel photo-sharing platform: upload trip photos, organize albums, and browse others' journeys. Later: posts and travel guides, then follows and feeds.

**Status:** M0 — infrastructure. See [`docs/roadmap.md`](docs/roadmap.md).

## Docs
- [Charter](docs/charter.md) — scope, phases, product standards
- [Architecture](docs/architecture.md) — stack, layering, directory layout, upload flow, operations
- [Security checklist](docs/security-checklist.md)
- [Roadmap](docs/roadmap.md)
- [Decisions (ADRs)](docs/decisions/README.md)
- [Workflow](docs/workflow.md)

## Names: `travelapp` vs. the brand
- **`travelapp`** is the internal code name. It is used for the Python package, the Docker Compose project, service names, buckets and database names. It does not change when the product gets its public name.
- **The brand name** (not chosen yet; Claude recommends deciding before M4 deployment, see ADR-0009) is what users see. It lives only in the `SITE_NAME` setting and in frontend copy, logo and legal pages. Code never hard-codes it.
- The GitHub repository stays `travel-app`.

See [ADR-0009](docs/decisions/0009-name-domain.md).

## Project layout
```
backend/      FastAPI API + Celery worker (one Python package: travelapp)
frontend/     Next.js web app
docs/         charter, architecture, roadmap, ADRs, security checklist
.env.example  every environment variable the services read, with local defaults
```
The full planned layout, and which roadmap item creates each part, is in [`docs/architecture.md`](docs/architecture.md) section 8.

## Getting started

### 1. Prerequisites
- **Git**
- **Docker** with Docker Compose v2 (`docker compose version` should work).
  - Windows: use WSL 2 and Docker Desktop with the WSL 2 backend; run every command below inside the WSL terminal.
  - macOS: Docker Desktop. Linux: Docker Engine + the Compose plugin.

For now nothing else is needed: PostgreSQL, Redis, MinIO and the app itself will run inside Docker. If a later M0 item (for example pre-commit hooks) needs a tool on your machine, it adds it here.

### 2. Get the code
```bash
git clone https://github.com/junhao-logan/travel-app.git
cd travel-app
```

### 3. Create your local config
```bash
cp .env.example .env
```
The defaults work for local development as-is. `.env` is ignored by git; never commit it.
For production, every password and secret must be regenerated (see the header of `.env.example`).

### 4. Start the services
_Not available yet._ The one-command start (`docker compose up`) is added by the next M0 item, "Docker Compose". Each M0 item adds its commands here when it lands, so this section only lists commands that work today.
