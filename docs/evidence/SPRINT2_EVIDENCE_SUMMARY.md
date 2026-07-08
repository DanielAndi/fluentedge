# Sprint 2 Evidence Summary

**Collected:** 2026-07-08  
**Collector:** Prompt 06 evidence synchronization pass

## Repository

- URL: https://github.com/DanielAndi/fluentedge
- Commit baseline: [`a282667`](https://github.com/DanielAndi/fluentedge/commit/a282667) with local evidence refresh edits pending commit
- Branch: `main`

## GitHub Project

- URL: https://github.com/users/DanielAndi/projects/4
- Project number: 4
- Manual view configuration completed: **Partially** (Kanban board and Backlog table screenshots captured; Evidence Review view still optional/recommended)

## Automated Verification

| Check | Command or workflow | Result | Evidence link |
|-------|---------------------|--------|---------------|
| Unit tests (fixtures) | `pytest tests/unit -m "not integration"` | pass (41 passed, 2 skipped) | Local run 2026-07-08; CI [run 28910958932](https://github.com/DanielAndi/fluentedge/actions/runs/28910958932) |
| Format check | `ruff format --check .` | pass | Local run 2026-07-08; CI run above |
| Lint | `ruff check .` | pass | Local run 2026-07-08; CI run above |
| Compose config | `docker compose -f infrastructure/compose.yaml config` | pass | [`ci-cd.md`](E-07-deployment-monitoring/ci-cd.md); CI job in run above |
| Docs validation | `python scripts/validate_docs.py` | pass; placeholder scan now reports only instructional references, not missing spec evidence placeholders | CI [Docs run 28910958996](https://github.com/DanielAndi/fluentedge/actions/runs/28910958996) |
| Container build + smoke | `Container` workflow | pass | [run 28910958927](https://github.com/DanielAndi/fluentedge/actions/runs/28910958927) |
| GitHub governance audit | `scripts/export_project_evidence.sh` | pass | [`github-audit.md`](E-09-github-governance/github-audit.md) |
| Secret scan | `gitleaks/gitleaks-action@v2` in CI | pass on `main` | CI run 28910958932 |
| Dependency scan | `pip-audit` in CI | warn (known `mlflow`/`pyarrow` advisories; non-blocking) | CI artifacts on run 28910958932 |
| Manual local evidence bundle | `Manual Local Evidence` workflow | not run | Trigger manually from Actions tab |

## Requirements Coverage

| Requirement IDs | Implementation | Test | Evidence |
|-----------------|----------------|------|----------|
| FR-DI-001–007 | [`ml/data/schema.py`](https://github.com/DanielAndi/fluentedge/blob/db1a67cd68efb402386870d66422a4a9617c61ed/ml/data/schema.py), [`ml/data/validate.py`](https://github.com/DanielAndi/fluentedge/blob/db1a67cd68efb402386870d66422a4a9617c61ed/ml/data/validate.py) | `tests/unit/test_validate.py`, `tests/unit/test_split.py` | [`E-04-data/README.md`](E-04-data/README.md), [`docs/data/dataset_card.md`](https://github.com/DanielAndi/fluentedge/blob/db1a67cd68efb402386870d66422a4a9617c61ed/docs/data/dataset_card.md) |
| FR-ML-001–008 | [`ml/pipeline/local_pipeline.py`](https://github.com/DanielAndi/fluentedge/blob/db1a67cd68efb402386870d66422a4a9617c61ed/ml/pipeline/local_pipeline.py), [`ml/models/train.py`](https://github.com/DanielAndi/fluentedge/blob/db1a67cd68efb402386870d66422a4a9617c61ed/ml/models/train.py) | `tests/unit/test_pipeline.py`, integration marker | [`E-06-training-evaluation/README.md`](E-06-training-evaluation/README.md), `artifacts/runs/467fb3aa/evaluation_report.json` |
| FR-INF-001–012 | [`infrastructure/compose.yaml`](https://github.com/DanielAndi/fluentedge/blob/db1a67cd68efb402386870d66422a4a9617c61ed/infrastructure/compose.yaml), [`infrastructure/sam/template.yaml`](https://github.com/DanielAndi/fluentedge/blob/db1a67cd68efb402386870d66422a4a9617c61ed/infrastructure/sam/template.yaml) | `tests/unit/test_storage.py`, compose config in CI | [`E-05-infrastructure/README.md`](E-05-infrastructure/README.md) |
| FR-API-001–007 | [`api/app/routers/`](https://github.com/DanielAndi/fluentedge/tree/db1a67cd68efb402386870d66422a4a9617c61ed/api/app/routers), [`api/static/index.html`](https://github.com/DanielAndi/fluentedge/blob/db1a67cd68efb402386870d66422a4a9617c61ed/api/static/index.html) | `tests/unit/test_predict.py` | [`E-08-ui-api/README.md`](E-08-ui-api/README.md), [`openapi.json`](E-08-ui-api/openapi.json), [`sample_response.json`](E-08-ui-api/sample_response.json) |
| FR-PM-001–009 | [`scripts/bootstrap_github.sh`](https://github.com/DanielAndi/fluentedge/blob/db1a67cd68efb402386870d66422a4a9617c61ed/scripts/bootstrap_github.sh), GitHub Project #4 | `scripts/audit_github_setup.sh` | [`github-audit.md`](E-09-github-governance/github-audit.md), issues [#1](https://github.com/DanielAndi/fluentedge/issues/1)–[#9](https://github.com/DanielAndi/fluentedge/issues/9) |
| FR-PM-006, FR-INF-011–012 | [`.github/workflows/ci.yml`](https://github.com/DanielAndi/fluentedge/blob/db1a67cd68efb402386870d66422a4a9617c61ed/.github/workflows/ci.yml) | CI, Container, Docs workflows | [`ci-cd.md`](E-07-deployment-monitoring/ci-cd.md) |
| NFR-MAINT-001 | ruff + pytest in CI | CI quality job | [CI run 28910958932](https://github.com/DanielAndi/fluentedge/actions/runs/28910958932) |
| NFR-SEC-001–003 | gitleaks + pip-audit in CI | CI security steps | CI run above |
| NFR-OBS-001–002 | Prometheus + Grafana compose services | partial (stack not running during this pass) | [`monitoring/grafana/dashboards/fluentedge-operations.json`](https://github.com/DanielAndi/fluentedge/blob/db1a67cd68efb402386870d66422a4a9617c61ed/monitoring/grafana/dashboards/fluentedge-operations.json) |
| NFR-REL-001–002 | model registry + rollback scripts | partial | Issue [#8](https://github.com/DanielAndi/fluentedge/issues/8) still open |

## Merged pull requests (CI/tooling)

| PR | Title | URL |
|----|-------|-----|
| #10 | Bump `actions/upload-artifact` 4 → 7 | https://github.com/DanielAndi/fluentedge/pull/10 |
| #13 | Bump `actions/checkout` 4 → 7 | https://github.com/DanielAndi/fluentedge/pull/13 |
| #14 | Bump `actions/setup-python` 5 → 6 | https://github.com/DanielAndi/fluentedge/pull/14 |

## Missing Evidence

- [ ] Branch protection settings screenshot (optional if rules not enabled on account plan)
- [ ] GitHub Project saved views: Roadmap, Evidence Review (confirm in web UI, optional/recommended)
- [ ] Manual Local Evidence workflow run + artifact download (optional)
- [ ] Written Confluence waiver if syllabus requires Confluence page

## Captured 2026-07-08

- [x] Architecture diagrams are embedded as Mermaid in the design specification and documented in `docs/evidence/E-01-architecture/README.md`
- [x] Requirements review / backlog table screenshot
- [x] Performance latency report + screenshot
- [x] EDA / evaluation screenshot
- [x] Health-check output (text + screenshot)
- [x] MLflow, Grafana, Prometheus, learner UI screenshots refreshed from local stack
- [x] GitHub Actions CI screenshot
- [x] Project board capture + repository overview + fields export
- [x] Traceability / evidence index screenshot
- [x] Final submission document (`docs/evidence/E-10-final-review/SPRINT2_FINAL_SUBMISSION.md`)

## Known Limitations

- Local UI, MLflow, Grafana, and Prometheus screenshots were refreshed from a running Docker Compose stack during the evidence audit.
- All nine Sprint 2 GitHub issues remain **open**; acceptance criteria are not fully satisfied (monitoring, manual Project views, final evidence review).
- Training metrics on synthetic fixtures (macro F1 1.0) demonstrate pipeline function only, not real-world accuracy.
- `pip-audit` reports known advisories for pinned `mlflow==2.18.0` dependencies; CI treats the scan as non-blocking.
- Three Dependabot PRs remain open (#11 Python 3.14, #12 gitleaks v3, #15 mlflow 3.x) and are intentionally unmerged.
- The design specification no longer has unresolved evidence placeholders; remaining placeholder-scan matches are instructional references in prompts/checklists.
