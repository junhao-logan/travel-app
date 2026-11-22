# backend

Python 3.12 + FastAPI API server **and** Celery worker. Both run from the same code
and the same Docker image, started with different commands (ADR-0003, ADR-0007):
the worker reuses the same `services/` and `repositories/` as the API.

> Status: placeholder. Filled in by the M0 roadmap item "后端骨架" (backend skeleton).
> See [`docs/roadmap.md`](../docs/roadmap.md).

## Planned layout

The Python package uses the code name `travelapp` (ADR-0009) and the **src layout**,
so tests always import the installed package, i.e. the same code that ships in the image.

```
backend/
├── src/travelapp/
│   ├── api/           request parsing and responses only
│   ├── services/      business logic and permission checks
│   ├── repositories/  the only place that queries the database
│   ├── models/        SQLAlchemy ORM models
│   ├── schemas/       Pydantic request/response models
│   ├── core/          config, logging, errors, storage.py, email.py
│   └── workers/       Celery tasks
├── tests/
└── migrations/        Alembic
```

Layering rules: [`docs/architecture.md`](../docs/architecture.md) section 2.
