# CI/CD Evidence

**Date:** 2026-07-08  
**Requirements:** FR-INF-011, FR-INF-012, FR-PM-006, NFR-MAINT-001

## Workflow files

| Workflow | File |
|----------|------|
| CI | [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) |
| Container | [`.github/workflows/container.yml`](../../../.github/workflows/container.yml) |
| Docs | [`.github/workflows/docs.yml`](../../../.github/workflows/docs.yml) |
| Manual local evidence | [`.github/workflows/manual-local-evidence.yml`](../../../.github/workflows/manual-local-evidence.yml) |
| Dependabot | [`.github/dependabot.yml`](../../../.github/dependabot.yml) |
| Branch protection guide | [`docs/project-management/branch-protection.md`](../../project-management/branch-protection.md) |

## Expected workflow names

| GitHub Actions workflow name | Trigger |
|------------------------------|---------|
| `CI` | Pull requests and pushes to `main` |
| `Container` | Pull requests and pushes to `main` |
| `Docs` | Pull requests and pushes to `main` (Markdown paths) |
| `Manual Local Evidence` | Manual (`workflow_dispatch`) |

## Commands run

Run from repository root. Host Python must be 3.11, or use the Docker one-liners below.

```bash
# Locked dependency install (CI equivalent)
docker run --rm -v "$(pwd):/app" -w /app python:3.11-slim bash -c \
  "pip install -q --upgrade pip && pip install -r requirements-dev.lock && pip install -e ."

# Format, lint, tests, coverage, vulnerability scan
docker run --rm -v "$(pwd):/app" -w /app python:3.11-slim bash -c \
  "pip install -q --upgrade pip && pip install -r requirements-dev.lock && pip install -e . && \
   ruff format --check . && ruff check . && \
   pytest tests/unit -v --junitxml=test-results/junit.xml \
     --cov=api --cov=ml --cov-report=term-missing --cov-report=xml:coverage.xml && \
   pip-audit -r requirements-dev.lock"

# Compose config validation (FR-INF-011)
docker compose -f infrastructure/compose.yaml config

# Documentation validation
python3 scripts/validate_docs.py
python3 scripts/validate_docs.py --placeholders-only --report-file placeholder-report.md

# Container build and smoke test
docker build -f api/Dockerfile -t fluentedge-api:local .
docker run -d --name fluentedge-smoke \
  -e STORAGE_BACKEND=filesystem \
  -e FILESYSTEM_STORAGE_ROOT=/tmp/storage \
  -e APPROVED_MODEL_URI=models:/fluentedge-baseline/1 \
  -e APPROVED_MODEL_VERSION=1 \
  -p 8000:8000 fluentedge-api:local
curl -fsS http://localhost:8000/health
docker rm -f fluentedge-smoke
```

## GitHub Actions run URLs

| Workflow | Run URL |
|----------|---------|
| CI | https://github.com/DanielAndi/fluentedge/actions/runs/28910958932 |
| Container | https://github.com/DanielAndi/fluentedge/actions/runs/28910958927 |
| Docs | https://github.com/DanielAndi/fluentedge/actions/runs/28910958996 |
| Manual Local Evidence | Not run yet — trigger from Actions → **Manual Local Evidence** |

Commit verified: [`db1a67c`](https://github.com/DanielAndi/fluentedge/commit/db1a67cd68efb402386870d66422a4a9617c61ed)

## Results

| Check | Status | Notes |
|-------|--------|-------|
| Workflow YAML syntax | pass | Validated locally |
| Format check (`ruff format --check`) | pass | Verified locally 2026-07-08 |
| Lint (`ruff check`) | pass | Verified locally 2026-07-08 |
| Unit tests + JUnit/coverage | pass | 41 passed, 2 skipped, 1 integration excluded |
| `pip-audit` | warn | Known `mlflow==2.18.0` / `pyarrow` CVEs; non-blocking in CI |
| Gitleaks secret scan | pass | [CI run 28910958932](https://github.com/DanielAndi/fluentedge/actions/runs/28910958932) |
| Compose config | pass | `.env` optional for CI validation |
| Container build + smoke | pass | [Container run 28910958927](https://github.com/DanielAndi/fluentedge/actions/runs/28910958927) |
| Docs validation | pass | 18 Markdown files; placeholders tracked separately |
| Dependabot config | pass | `.github/dependabot.yml` present |

## Merged CI dependency PRs

- https://github.com/DanielAndi/fluentedge/pull/10 (`upload-artifact` v7)
- https://github.com/DanielAndi/fluentedge/pull/13 (`checkout` v7)
- https://github.com/DanielAndi/fluentedge/pull/14 (`setup-python` v6)

## Remaining manual evidence

See [`../MANUAL_SCREENSHOT_CHECKLIST.md`](../MANUAL_SCREENSHOT_CHECKLIST.md) for the full list. Highlights:

- [x] Grafana dashboard screenshot
- [x] MLflow run screenshot
- [ ] GitHub Actions / Project board / saved-view screenshots from authenticated browser
- [ ] Branch protection screenshot (if enabled)
- [ ] Run **Manual Local Evidence** workflow and record artifact URL

## Checks that only run on GitHub

- **Gitleaks secret scan** (`gitleaks/gitleaks-action@v2`) — uses GitHub token and runner environment.
- **Dependabot PRs** — scheduled dependency updates require GitHub App integration.
- **Branch protection enforcement** — configured in repository settings, not in workflow files.
- **Optional AWS deployment (FR-INF-012)** — intentionally omitted; no cloud resources created automatically.

## Commit and push to trigger CI

```bash
git add .github/workflows/ci.yml \
        .github/workflows/container.yml \
        .github/workflows/docs.yml \
        .github/workflows/manual-local-evidence.yml \
        .github/dependabot.yml \
        requirements-dev.lock \
        scripts/validate_docs.py \
        docs/project-management/branch-protection.md \
        docs/evidence/E-07-deployment-monitoring/ci-cd.md

git commit -m "$(cat <<'EOF'
Add GitHub Actions CI/CD baseline for local validation evidence.

Covers FR-INF-011, FR-PM-006, and NFR-MAINT-001 with lint, test, security,
container, and documentation workflows without AWS deployment.
EOF
)"

git push origin HEAD
```

After push, open **Actions** on GitHub and confirm `CI`, `Container`, and `Docs` workflows run on the branch or pull request.
