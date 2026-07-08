# AWS SAM Local Adapter (FR-INF-004)

The **primary** FluentEdge local demo uses the FastAPI container (`http://localhost:8000`). This SAM project is an **optional** API Gateway / Lambda compatibility layer for coursework evidence.

## Prerequisites

- AWS SAM CLI installed (`sam --version`)
- Docker running (SAM uses containers for `python3.11` runtime)

## Commands

From the repository root:

```bash
make sam-build
# equivalent: sam build --use-container -t infrastructure/sam/template.yaml
make sam-local
# or
sam build -t infrastructure/sam/template.yaml
sam local start-api -t infrastructure/sam/template.yaml --port 3001
```

Test:

```bash
curl http://127.0.0.1:3001/health
```

## Limitations

- The SAM `/health` handler returns adapter status only; it does **not** proxy to the full Docker stack by default.
- `/predict` returns `501` with guidance to use FastAPI. A future phase may add HTTP proxying to the API container.
- `sam local` runs on the host network namespace; use `host.docker.internal:8000` (or Linux equivalent) if proxying is added.
- **Do not deploy** this template to AWS without explicit authorization (NFR-COST-001).

## Design decision

FastAPI is authoritative for the class prototype (see design spec §6.5). SAM satisfies FR-INF-004 local compatibility evidence without duplicating inference logic.
