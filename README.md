# FluentEdge

Local-first, AWS-compatible MLOps prototype for AI-powered speaking feedback (SWE-452).

## Prerequisites

- Docker Engine with Compose
- Python 3.11 (host) or use containerized API only
- AWS CLI (for bootstrap against LocalStack)
- AWS SAM CLI (optional, for FR-INF-004 local adapter)
- `make` and Bash

## Quick start

```bash
cp .env.example .env
make setup
make up
make bootstrap    # safe to rerun
make health
```

### Service URLs

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| MLflow | http://localhost:5000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (admin/admin) |
| LocalStack S3 | http://localhost:4566 |

## Shutdown

```bash
make down
make cleanup      # stops stack and runs retention cleanup
```

To remove volumes (destructive):

```bash
REMOVE_VOLUMES=1 ./scripts/cleanup_local.sh
```

## Storage backends

Set `STORAGE_BACKEND=s3` (default with Compose) or `STORAGE_BACKEND=filesystem` for offline/CI fallback. Credentials in `.env.example` use LocalStack placeholders only (`test`/`test`).

## Optional SAM local adapter

```bash
make sam-build       # uses --use-container when host lacks Python 3.11
make sam-local
curl http://127.0.0.1:3001/health
```

See `infrastructure/sam/README.md` for limitations.

## Tests

```bash
make test-docker     # Python 3.11 container (host 3.13 is not supported for local pip install)
make test-s3         # S3 adapter tests against LocalStack
make test-ml         # data/ML unit tests
make test-ml-integration  # full pipeline + MLflow (requires stack up)
make retention-test
```

## ML pipeline

```bash
make fixtures
make data-validate
make pipeline-local
make approve-model MODEL_VERSION=1
```

After training, the pipeline writes `artifacts/production/model.joblib` for API inference.

## API demo

```bash
make health
make test-api
curl -F "expected_phrase=the quick brown fox" -F "file=@tests/fixtures/synthetic/clip_000.wav" http://localhost:8000/predict
```

Open http://localhost:8000 for the learner UI.

See `docs/evidence/E-04-data/` and `docs/evidence/E-06-training-evaluation/`.

## Architecture

See `FluentEdge_Sprint2_Design_and_Requirements_Specification.md` and `docs/evidence/E-05-infrastructure/`.

## Windows notes

Use Git Bash or WSL for `make` and shell scripts. PowerShell equivalents:

```powershell
docker compose -f infrastructure/compose.yaml up -d --build
python -m pytest tests/unit -v
```

## Requirement traceability

Infrastructure phase covers FR-INF-001–012 and related NFRs. Evidence is recorded under `docs/evidence/E-05-infrastructure/`.
