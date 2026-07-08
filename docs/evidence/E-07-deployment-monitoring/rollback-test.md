# Rollback baseline evidence

**Date:** 2026-07-08

## Approved production model

- Model: `fluentedge-baseline`
- Version: `1`
- Stage: `Production`
- Tags: `approval_status=approved`, `approved_by=project-owner`

## Verification command

```bash
python scripts/approve_model.py 1 --tracking-uri http://localhost:5000
```

## Rollback policy

A failed candidate does not replace the approved model. The API loads the versioned artifact from MLflow / production fallback (`artifacts/production/model.joblib`).

## Evidence

Re-approval of version 1 succeeded with production stage intact. Prior artifact checksum recorded in MLflow run parameters.
