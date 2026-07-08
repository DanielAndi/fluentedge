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
| 1 | Local architecture diagram | Export Mermaid from spec §2.4/§2.5 or draw.io | `docs/evidence/E-01-architecture/local-architecture.png` | E-01 |
| 2 | AWS target architecture diagram | Export spec §2.5 Mermaid or draw.io | `docs/evidence/E-01-architecture/aws-target-architecture.png` | E-01 |
| 3 | GitHub Project — field list | Project → Settings → Fields | `docs/evidence/E-09-github-governance/project-fields.png` | E-02, E-09 |
| 4 | GitHub Project — Sprint board | Board view filtered to Sprint 2 | `docs/evidence/E-09-github-governance/project-board-sprint2.png` | E-02, E-09 |
| 5 | GitHub Project — Evidence Review view | Filter Status = In Review or empty Evidence | `docs/evidence/E-09-github-governance/project-evidence-review.png` | E-09 |
| 6 | Requirements review | Open issue [#1](https://github.com/DanielAndi/fluentedge/issues/1) or design spec PDF export preview | `docs/evidence/E-02-requirements/requirements-review.png` | E-02 |
| 7 | MLflow experiment + registered model | http://localhost:5000 — show run metrics and `fluentedge-baseline` v1 | `docs/evidence/E-06-training-evaluation/mlflow-screenshot.png` | E-06 |
| 8 | Grafana operations dashboard | http://localhost:3000 — `fluentedge-operations` dashboard after traffic | `docs/evidence/E-07-deployment-monitoring/grafana-dashboard.png` | E-07, E-08 |
| 9 | Compose startup | `docker compose ps` or `make health` terminal output | `docs/evidence/E-05-infrastructure/health-check-output.png` | E-05, E-07 |
| 10 | Learner UI — successful prediction | http://localhost:8000 — phrase + fixture WAV + Analyze | `docs/evidence/E-08-ui-api/ui-screenshot.png` | E-08 |
| 11 | GitHub Actions — green CI run | Actions → latest `main` CI workflow | `docs/evidence/E-07-deployment-monitoring/actions-ci-green.png` | E-07 |
| 12 | Branch protection (if enabled) | Repo Settings → Rules | `docs/evidence/E-09-github-governance/branch-protection.png` | E-09 |
| 13 | Performance / latency | Run load test or capture p95 from test output | `docs/evidence/E-03-non-functional/performance.png` | E-03 |
| 14 | EDA or data validation summary | Notebook output or validation report chart | `docs/evidence/E-04-data/eda-screenshot.png` | E-04 |
| 15 | Rollback test | Document output from rollback/approval reversal test | `docs/evidence/E-07-deployment-monitoring/rollback-test.md` or `.png` | E-07, issue #8 |
| 16 | Final traceability review | Appendix A + open issues overview | `docs/evidence/E-10-final-review/traceability-review.png` | E-10 |

## Optional but recommended

| # | Subject | Save to |
|---|---------|---------|
| 17 | Manual Local Evidence workflow artifact listing | Reference URL in `ci-cd.md` |
| 18 | Prometheus targets healthy | `docs/evidence/E-07-deployment-monitoring/prometheus-targets.png` |
| 19 | Confluence page or instructor waiver email | Note in spec §10 (`Confluence waiver: instructor-approved GitHub-only evidence`) |

## After capture

1. Update [`SPRINT2_EVIDENCE_SUMMARY.md`](SPRINT2_EVIDENCE_SUMMARY.md) — move items from **Missing Evidence** to completed.
2. Update Appendix D statuses in `FluentEdge_Sprint2_Design_and_Requirements_Specification.md`.
3. Replace remaining `[INSERT IMAGE PATH]` placeholders in the specification with the relative paths above.
4. Re-run `python scripts/validate_docs.py --placeholders-only` and confirm the count drops.
