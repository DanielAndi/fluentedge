# Sprint 4 Validation Evidence

Generated July 20, 2026 local time with Python 3.11 in the checked-in application image.

## Commands run

```bash
python scripts/run_sprint4_validation.py
ruff format --check .
ruff check .
pytest tests/unit -v -m "not integration" --junitxml=... --cov=api --cov=ml
pip-audit -r requirements-dev.lock
python scripts/generate_artifact_inventory.py
```

## Results

| Gate | Result | Evidence |
|---|---|---|
| Nonempty speaker partitions | Pass: six speakers allocate 4 train, 1 validation, 1 test | `tests/unit/test_split.py`, `junit.xml` |
| Warm prediction performance | Pass: 30 requests, p95 84.749 ms, target 2,000 ms | `validation-report.json` |
| Health performance | Pass: 30 requests, p95 36.732 ms, target 250 ms | `validation-report.json` |
| Concurrency | Pass: five simultaneous 200 responses, unique IDs, zero leftover uploads | `validation-report.json` |
| Controlled dependency failure | Pass: injected storage and model-load failures return controlled 503 responses | `unit-tests.txt`, `junit.xml` |
| Rollback | Pass: mismatched candidate rejected; approved SHA-256 restored and model loaded | `validation-report.json` |
| Startup reliability | Pass: two consecutive API, storage, model, and health cycles | `startup-cycle-1.log`, `startup-cycle-2.log` |
| Full Compose health | Pass: Docker, S3, API, MLflow, Prometheus, and Grafana | `full-stack-health.txt` |
| Local screenshots | Pass: successful learner prediction, MLflow runs, populated Grafana dashboard, Prometheus target up | E-06, E-07, and E-08 PNG files |
| GitHub Actions | Pass: CI, Container, and Docs workflows successful | E-07 `actions-ci-sprint4.png` and run links below |
| Unit tests | Pass: 45 passed, 2 LocalStack-only tests skipped, 1 integration test deselected | `unit-tests.txt`, `junit.xml` |
| Format and lint | Pass: 57 files formatted; Ruff check passed | `quality-checks.txt` |
| Coverage | 78% combined API/ML statement coverage | `coverage.xml`, `unit-tests.txt` |
| Dependency audit | Blocked: 32 findings in MLflow 2.18.0 and pyarrow 18.1.0 | `dependency-audit.txt`, `dependency-audit.json` |

## Method

`scripts/run_sprint4_validation.py` starts the FastAPI application twice in isolated local processes. It serves the checked-in production model through the real inference path and uses filesystem storage. A local health stub represents the MLflow health endpoint so health latency measures the API path rather than a missing external service. The performance clip is a synthetic functional fixture; the results do not establish real-world model quality.

Run the evidence again with:

```bash
make sprint4-validation
```

The dependency report is evidence of an unresolved gate, not a risk acceptance. Upgrading MLflow/pyarrow or signing an explicit acceptance decision remains required.

## Screenshot Record

Captured July 20, 2026 local time from the running Compose stack:

- `docs/evidence/E-08-ui-api/ui-screenshot.png`: successful fixture prediction with score, label, confidence, feedback, and request ID.
- `docs/evidence/E-06-training-evaluation/mlflow-screenshot.png`: `fluentedge-training` runs and registered `fluentedge-baseline` model links.
- `docs/evidence/E-07-deployment-monitoring/grafana-dashboard.png`: request rate, p95 latency, dependency health, and prediction-label activity.
- `docs/evidence/E-07-deployment-monitoring/prometheus-targets.png`: `fluentedge-api` target state `UP`.
- `docs/evidence/E-07-deployment-monitoring/actions-ci-sprint4.png`: successful CI lint/test/security and Compose jobs for `e68e8f0`.

GitHub run links:

- CI: https://github.com/DanielAndi/fluentedge/actions/runs/29830461177
- Container: https://github.com/DanielAndi/fluentedge/actions/runs/29830461158
- Docs: https://github.com/DanielAndi/fluentedge/actions/runs/29830461275
