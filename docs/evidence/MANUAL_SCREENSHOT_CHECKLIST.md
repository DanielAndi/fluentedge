# Manual Screenshot Checklist

**Purpose:** Capture evidence that cannot be produced automatically during Prompt 06.  
**Save location:** Repository-relative paths below unless noted.

## Before you capture

1. Run `make up` (or `docker compose -f infrastructure/compose.yaml up -d`) and wait for healthy services.
2. Run `make pipeline-local` and `make approve-model MODEL_VERSION=1` if `/ready` reports `model_ready: false`.
3. Redact secrets, tokens, and private audio from every screenshot before commit.

## Required captures

| # | Subject | Steps | Save to | Related evidence |
|---|---------|-------|---------|------------------|
| 1 | GitHub Project — field list | Project → Settings → Fields | `docs/evidence/E-09-github-governance/project-fields.png` | E-02, E-09 |
| 2 | GitHub Project — Sprint board | Board view filtered to Sprint 2 | `docs/evidence/E-09-github-governance/project-board-sprint2.png` | E-02, E-09 |
| 3 | GitHub Project — Evidence Review view | Filter Status = In Review or empty Evidence | `docs/evidence/E-09-github-governance/project-evidence-review.png` | E-09 |
| 4 | Requirements review | Open issue [#1](https://github.com/DanielAndi/fluentedge/issues/1) or design spec PDF export preview | `docs/evidence/E-02-requirements/requirements-review.png` | E-02 |
| 5 | MLflow experiment + registered model | http://localhost:5000 — show run metrics and `fluentedge-baseline` v1 | `docs/evidence/E-06-training-evaluation/mlflow-screenshot.png` | E-06 |
| 6 | Grafana operations dashboard | http://localhost:3000 — `fluentedge-operations` dashboard after traffic | `docs/evidence/E-07-deployment-monitoring/grafana-dashboard.png` | E-07, E-08 |
| 7 | Compose startup | `docker compose ps` or `make health` terminal output | `docs/evidence/E-05-infrastructure/health-check-output.png` | E-05, E-07 |
| 8 | Learner UI — successful prediction | http://localhost:8000 — phrase + fixture WAV + Analyze | `docs/evidence/E-08-ui-api/ui-screenshot.png` | E-08 |
| 9 | GitHub Actions — green CI run | Actions → latest `main` CI workflow | `docs/evidence/E-07-deployment-monitoring/actions-ci-green.png` | E-07 |
| 10 | Branch protection (if enabled) | Repo Settings → Rules | `docs/evidence/E-09-github-governance/branch-protection.png` | E-09 |
| 11 | Performance / latency | Run load test or capture p95 from test output | `docs/evidence/E-03-non-functional/performance.png` | E-03 |
| 12 | EDA or data validation summary | Notebook output or validation report chart | `docs/evidence/E-04-data/eda-screenshot.png` | E-04 |
| 13 | Rollback test | Document output from rollback/approval reversal test | `docs/evidence/E-07-deployment-monitoring/rollback-test.md` or `.png` | E-07, issue #8 |
| 14 | Final traceability review | Appendix D evidence index + final submission summary | `docs/evidence/E-10-final-review/traceability-review.png` | E-10 |

## Captured from `/home/danielg/Downloads/evidence`

| Source file | Saved evidence path | Related evidence |
|---|---|---|
| `kanbanboard.png` | `docs/evidence/E-09-github-governance/project-board-sprint2.png` | E-02, E-09 |
| `backlog.png` | `docs/evidence/E-02-requirements/requirements-review.png` | E-02 |
| `clievidence.png` | `docs/evidence/E-07-deployment-monitoring/actions-ci-green.png` | E-03, E-07 |
| `repository.png` | `docs/evidence/E-09-github-governance/repository-overview.png` | E-09 |

## Optional but recommended

| # | Subject | Save to |
|---|---------|---------|
| 17 | Manual Local Evidence workflow artifact listing | Reference URL in `ci-cd.md` |
| 18 | Prometheus targets healthy | `docs/evidence/E-07-deployment-monitoring/prometheus-targets.png` |
| 19 | Confluence page or instructor waiver email | Note in spec §10 (`Confluence waiver: instructor-approved GitHub-only evidence`) |

## After capture

1. Update [`SPRINT2_EVIDENCE_SUMMARY.md`](SPRINT2_EVIDENCE_SUMMARY.md) — move items from **Missing Evidence** to completed.
2. Update Appendix D statuses in `FluentEdge_Sprint2_Design_and_Requirements_Specification.md`.
3. Confirm the specification points to the relative evidence paths above.
4. Re-run `python scripts/validate_docs.py --placeholders-only` and confirm the count drops.
