# E-08 UI and API Evidence

**Date:** 2026-07-06  
**Requirements:** FR-API-001–007, NFR-PERF-001–002, NFR-SEC-002, NFR-PRIV-002, NFR-OBS-001–002, NFR-USAB-001

## Commands run

```bash
make up
make test-api          # 16 passed
curl http://localhost:8000/ready
curl -F "expected_phrase=the quick brown fox" -F "file=@tests/fixtures/synthetic/clip_000.wav" http://localhost:8000/predict
curl http://localhost:8000/openapi.json -o docs/evidence/E-08-ui-api/openapi.json
```

## Results

| Check | Status | Notes |
|-------|--------|-------|
| Contract tests | pass | 16/16 |
| `/ready` | pass | `model_ready: true`, version 1 |
| Live `/predict` | pass | label `pass`, confidence ~0.96 |
| OpenAPI export | pass | `docs/evidence/E-08-ui-api/openapi.json` |
| UI | manual | Open http://localhost:8000 and capture screenshot |

## Manual browser checks

1. Open http://localhost:8000
2. Enter phrase `the quick brown fox`
3. Upload `tests/fixtures/synthetic/clip_000.wav`
4. Click **Analyze** and verify score, label, confidence, feedback, request ID
5. Save screenshot to `docs/evidence/E-08-ui-api/ui-screenshot.png`

## Artifacts

- `api/static/index.html`
- `docs/evidence/E-08-ui-api/sample_request.md`
- `docs/evidence/E-08-ui-api/sample_response.json` (live capture)
- `docs/evidence/E-08-ui-api/openapi.json`

## Notes

- Production model fallback uses `artifacts/production/model.joblib` when MLflow artifact files are absent from the shared volume.
- Re-run `make pipeline-local` after training to refresh the production artifact.
