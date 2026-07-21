# Sprint 4 Closeout

**Owner:** Daniel Grijalva<br>
**Target date:** July 20, 2026<br>
**Status date:** July 20, 2026 local time<br>
**GitHub Project:** FluentEdge MLOps #4

## Scope and Results

| Work item | Requirement IDs | Acceptance criteria | Evidence | Status |
|---|---|---|---|---|
| Correct speaker-aware partition allocation | FR-DI-006, NFR-REL-003 | Deterministic, speaker-disjoint train/validation/test partitions are nonempty when at least three groups exist | `ml/data/split.py`, `tests/unit/test_split.py`, E-11 JUnit | Done locally |
| Validate API and health performance | NFR-PERF-001, NFR-PERF-002 | At least 30 warm predictions at p95 <= 2 seconds and 30 health requests at p95 < 250 ms | E-11 `validation-report.json` | Done locally |
| Validate concurrency and cleanup | NFR-SCALE-001, NFR-PRIV-001 | Five simultaneous requests succeed with unique IDs and no leftover uploads | E-11 `validation-report.json` | Done locally |
| Validate controlled dependency failure | NFR-REL-001, FR-API-004 | Injected storage and model-load failures return stable HTTP 503 contracts | `tests/unit/test_predict.py`, E-11 JUnit | Done locally |
| Exercise SHA-256 rollback | NFR-REL-002, FR-ML-007 | Reject mismatched candidate, restore approved digest, and load restored model | E-11 `validation-report.json` | Done locally |
| Validate two clean starts | NFR-REL-003, FR-INF-008 | Two consecutive start, health, and readiness cycles pass | E-11 startup logs | Done locally |
| Refresh code-quality evidence | FR-PM-006, NFR-MAINT-001 | Python 3.11 format, lint, unit tests, JUnit, and coverage are stored | E-11 test and coverage files | Done locally |
| Inventory important artifacts | FR-INF-006, FR-ML-002, FR-ML-007 | Explicit SHA-256 digest exists for each listed artifact | E-11 `artifact-inventory.sha256` | Done locally |
| Validate on licensed public speech data | FR-DI-001, FR-DI-002, FR-ML-003 | Versioned licensed subset and completed source dataset card exist | `docs/data/dataset_card.md` records the gap | Blocked |
| Resolve dependency findings | NFR-SEC-003 | Findings are remediated or explicitly accepted by an authorized owner | E-11 dependency audit | Blocked |
| Reconcile GitHub issues and Project fields | FR-PM-001 through FR-PM-007 | Scope, checkboxes, notes, links, status, dates, and requirements are current remotely | This closeout is the prepared source record | Blocked by GitHub authentication |
| Capture current local-service screenshots | NFR-OBS-001, NFR-USAB-001 | Grafana, Prometheus, MLflow, and learner UI match this baseline | Fresh images under E-06 through E-08 | Done locally |
| Capture current GitHub Actions screenshot | FR-PM-006, NFR-MAINT-001 | CI page shows successful lint/test/security and Compose jobs | E-07 `actions-ci-sprint4.png` | Done publicly |
| Capture current GitHub Project screenshot | FR-PM-001, FR-PM-003 | Project screenshot matches Sprint 4 issues and fields | Historical Project images remain under E-09 | Blocked by GitHub authentication |
| Record and publish walkthrough | FR-PM-005, NFR-USAB-001 | Prototype, code, progress, and limitations are recorded at a shareable URL | Script exists in the Sprint 4 report | Owner action |
| Confirm Confluence replacement | FR-PM-001, FR-PM-002 | Instructor approval or Confluence page is attached | `confluence-replacement-waiver.md` | Awaiting approval |

## Completion Notes

- The split regression now produces 32 train, 8 validation, and 8 test clips for the balanced six-speaker fixture.
- Warm `/predict` p95 was 84.749 ms across 30 requests; `/health` p95 was 36.732 ms across 30 requests.
- Five simultaneous requests returned HTTP 200 with unique request IDs and zero residual upload files.
- Storage and model-load failures returned controlled HTTP 503 responses.
- The rollback exercise rejected a mismatched artifact and restored SHA-256 `c7016b8858bf0efa35c6f364cb2dc1307734d71c33975d299f8e8a0e5ae05e82`.
- Python 3.11 verification produced 45 passing tests, 2 LocalStack-only skips, and 78% combined coverage.
- The full Compose stack passed all six health checks; learner UI, MLflow, Grafana, and Prometheus screenshots were recaptured from that running stack.
- GitHub CI, Container, and Docs workflows completed successfully at `e68e8f0d766701f76747b221ebd70f2ffeb2ab62`; the public CI summary is captured under E-07.
- The fresh audit found 32 known vulnerabilities across MLflow 2.18.0 and pyarrow 18.1.0. No acceptance is implied.

## Challenges and Remaining Responsibilities

The local engineering work was constrained by synthetic-only data, an invalid GitHub CLI token, GitHub-only browser evidence, and dependency versions requiring a potentially breaking MLflow upgrade. Daniel Grijalva remains responsible for selecting and accepting the license for a public validation subset, approving any dependency risk decision, repairing GitHub authentication, updating Project #4, capturing current GitHub screenshots, recording/uploading the demonstration, and obtaining the Confluence-replacement decision.

## Deadlines

| Date | Deliverable | State |
|---|---|---|
| July 20, 2026 | Sprint 4 Markdown, PDF, local validation evidence, and closeout | Complete locally |
| Before submission | Push scoped commits; update GitHub Project; capture screenshots; upload video; attach shareable URL | Blocked/owner action |
| Before final model acceptance | Licensed public-data evaluation and dependency remediation or signed acceptance | Open |
| August 9, 2026 | Final reproducible release and presentation | Planned |

## GitHub Publication Blocker

`gh auth status` reports that the active `DanielAndi` token is invalid. No remote issue, Project, push, or Actions state is claimed. Repair and verify authentication before applying updates:

```bash
gh auth login -h github.com
gh auth status
gh auth refresh -s project
```
