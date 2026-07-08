# E-05 Infrastructure Evidence

**Date:** 2026-07-06  
**Requirements:** FR-INF-001–012, NFR-REL-001–003, NFR-SEC-001–003, NFR-PRIV-001–002, NFR-OBS-001–002, NFR-PORT-001, NFR-COST-001–002

## Commands run

```bash
docker compose -f infrastructure/compose.yaml config   # exit 0
make up                                               # all 5 services healthy
make bootstrap && make bootstrap                      # idempotent bucket setup
make health                                           # 6/6 checks passed
make test-docker                                      # 11 passed, 2 skipped (S3 needs host network)
make test-s3                                          # 2 passed against LocalStack
make retention-test                                   # deleted=1
sam build --use-container -t infrastructure/sam/template.yaml  # Build Succeeded
```

## Results

| Check | Status | Notes |
|-------|--------|-------|
| Compose config | pass | `infrastructure/compose.yaml` validates |
| Stack startup | pass | localstack, mlflow, api, prometheus, grafana healthy |
| Bootstrap idempotent | pass | buckets detected on second run |
| Health check | pass | model reported `not_ready` (expected before training) |
| Storage unit tests | pass | filesystem + S3 (host network) |
| Retention cleanup | pass | expired upload removed |
| SAM build | pass | requires `sam build --use-container` without host Python 3.11 |

## API health sample (2026-07-06)

```json
{
  "status": "ok",
  "model_ready": false,
  "dependencies": {
    "storage": {"status": "ok"},
    "mlflow": {"status": "ok"},
    "model": {"status": "not_ready"}
  }
}
```

## Related artifacts

- `infrastructure/compose.yaml`
- `scripts/healthcheck.sh`
- `scripts/bootstrap_local.sh`
- `monitoring/grafana/dashboards/fluentedge-operations.json`
- `infrastructure/sam/template.yaml`

## GitHub Issue

`[INSERT ISSUE LINK]` — pending remote repository and GitHub Project setup (FR-PM-001).
