# E-06 Training and Evaluation Evidence

**Date:** 2026-07-06  
**Requirements:** FR-ML-001–008, NFR-REL-002, NFR-MAINT-001–002

## Commands run

```bash
make pipeline-local
make test-ml-integration
make approve-model MODEL_VERSION=1
```

## Results

| Check | Status | Notes |
|-------|--------|-------|
| Pipeline local run | pass | winner: `logistic_regression` |
| Candidate comparison | pass | LR and RF both macro F1 1.0 on fixtures |
| MLflow registration | pass | `fluentedge-baseline` version 1 |
| Model card generated | pass | `artifacts/runs/467fb3aa/model_card.md` |
| Explicit approval | pass | version 1 → Production |

## Key outputs

- **Macro F1 (test):** 1.0 on synthetic fixtures (functional evidence only)
- **MLflow run:** http://localhost:5000/#/experiments/1
- **Evaluation report:** `artifacts/runs/467fb3aa/evaluation_report.json`
- **Model card:** `artifacts/runs/467fb3aa/model_card.md`

## Metric disclaimer

Macro F1 on synthetic fixtures demonstrates pipeline functionality, not real-world pronunciation accuracy.

## Next step

Set `APPROVED_MODEL_VERSION=1` in `.env` and implement API `/predict` loading from MLflow (Prompt 03).
