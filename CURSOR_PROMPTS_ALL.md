# FluentEdge Cursor Prompts

Use the prompts in order. Each section is also available as a separate file in `prompts/`.

---

# Cursor Prompt 00 - Master Implementation Orchestrator

Copy everything below into Cursor Agent mode from the root of the FluentEdge repository.

---

You are the lead software, ML, and DevOps engineer for **FluentEdge**, a solo SWE-452 class project. Read `docs/design/FluentEdge_Sprint2_Design_and_Requirements_Specification.md` before changing any files. If the document is stored elsewhere, locate it first.

## Goal

Create a complete, local-first AWS-compatible MLOps prototype for AI-powered speaking feedback. The required demo must run locally without paid AWS resources. The architecture must remain portable to AWS.

## Non-negotiable constraints

1. Do not create or deploy real AWS resources unless I explicitly authorize a cloud deployment in a later message.
2. Do not read, print, commit, or expose credentials, access keys, GitHub tokens, or private audio.
3. Do not overwrite existing working files without first inspecting them and explaining the change.
4. Prefer small, reviewable phases and commits.
5. Use Python 3.11 unless the repository already specifies a compatible version.
6. Use Docker Compose for the local stack.
7. Use GitHub Issues and GitHub Projects as the approved Jira replacement.
8. Keep Confluence references in the documentation unless I provide written approval to replace Confluence.
9. Use requirement IDs from the design document in code comments only where useful, but always include them in tests, issue bodies, pull requests, and evidence reports.
10. Every generated script must be safe to rerun or must detect and report existing resources.

## Required local architecture

- FastAPI API and inference service.
- LocalStack for S3-compatible local object storage; use only supported baseline services and provide a filesystem fallback adapter.
- MLflow for experiment tracking, model versioning, and approval state.
- Prometheus for metrics.
- Grafana for dashboards.
- Docker Compose to coordinate services.
- AWS SAM CLI project for an optional local API Gateway/Lambda-compatible adapter.
- Local training and evaluation pipeline that can be mapped to SageMaker-compatible scripts or local mode.
- GitHub Actions for tests, linting, security checks, Compose validation, and image build.

## First response requirements

Before editing files:

1. Inspect the repository tree, Git status, existing Python configuration, Docker files, workflows, and documentation.
2. Compare the current repository with the design specification.
3. Produce a phased implementation plan with:
   - Files to create or modify.
   - Requirement IDs covered.
   - Commands that will be run.
   - Risks and assumptions.
   - Manual actions that cannot be automated.
4. Ask only the minimum blocking questions. Do not ask about details already defined in the specification.
5. Wait for approval before executing destructive or external operations.

## Implementation phases

1. Repository and configuration baseline.
2. Local infrastructure and health checks.
3. Data validation and training pipeline.
4. API and minimal UI.
5. Monitoring and rollback.
6. GitHub CLI and GitHub Project configuration.
7. GitHub Actions CI/CD.
8. Evidence collection and documentation synchronization.

## Definition of done

The project is complete when:

- `docker compose up -d` or the documented equivalent starts the local stack.
- A health-check script verifies all required services.
- Synthetic fixture data can run through validation, training, evaluation, registration, and local inference.
- `/health` and `/predict` pass automated tests.
- MLflow contains a versioned model and approval metadata.
- Prometheus and Grafana display required metrics.
- GitHub Actions pass.
- GitHub Issues and the GitHub Project contain the sprint work and evidence links.
- The design document's Appendix D is updated with real evidence.

Do not claim completion until the applicable commands and tests have actually run successfully.

---

# Cursor Prompt 01 - Local AWS-Compatible Infrastructure

Copy everything below into Cursor Agent mode after Prompt 00 has been approved.

---

Implement the local AWS-compatible infrastructure defined in the FluentEdge design specification.

## Scope

Cover at least these requirements:

- FR-INF-001 through FR-INF-012.
- NFR-REL-001 through NFR-REL-003.
- NFR-SEC-001 through NFR-SEC-003.
- NFR-PRIV-001 and NFR-PRIV-002.
- NFR-OBS-001 and NFR-OBS-002.
- NFR-PORT-001.
- NFR-COST-001 and NFR-COST-002.

## Required deliverables

Create or update:

```text
infrastructure/
├── compose.yaml
├── localstack/
│   └── init-aws.sh
├── sam/
│   ├── template.yaml
│   ├── samconfig.toml.example
│   └── functions/
├── terraform/
│   └── README.md
monitoring/
├── prometheus/prometheus.yml
└── grafana/
    ├── provisioning/
    └── dashboards/
scripts/
├── bootstrap_local.sh
├── healthcheck.sh
├── cleanup_local.sh
└── verify_retention.py
.env.example
Makefile
```

Adapt the paths if the repository already has an established structure.

## Docker Compose services

Define these services with health checks and named volumes:

1. `localstack`
   - Baseline service: S3.
   - Use a fixed local region such as `us-west-2`.
   - Initialize required buckets with a safe idempotent script.
   - Do not depend on LocalStack features that require a paid license for the minimum demo.
2. `mlflow`
   - Local tracking server.
   - SQLite or file backend is acceptable for the class prototype.
   - Use a persistent volume.
3. `api`
   - Build from the repository's FastAPI Dockerfile.
   - Do not fail permanently before a model exists; health output must distinguish service health from model readiness.
4. `prometheus`
   - Scrape the API metrics endpoint.
5. `grafana`
   - Provision a Prometheus data source and a FluentEdge dashboard.

Optional services may be added only when they directly support the specification and do not make startup fragile.

## Storage adapter

Implement an application storage interface with:

- `S3Storage` configured by endpoint URL, region, bucket, and credentials from environment variables.
- `FilesystemStorage` fallback for environments where LocalStack is unavailable.
- Generated object keys rather than client-controlled paths.
- Cleanup support for expired demo audio.
- Unit tests for both adapters.

Use safe local placeholder credentials such as `test` only in `.env.example`; never store real keys.

## AWS SAM local adapter

Create a small AWS SAM project that:

- Defines an API Gateway-compatible route for `/health` and either `/predict` or a proxy adapter.
- Uses a Lambda container or Python function that calls the shared application code.
- Can run with `sam build` and `sam local start-api`.
- Is clearly marked optional if the primary local demo calls FastAPI directly.
- Includes commands and limitations in `infrastructure/sam/README.md`.

Do not deploy the SAM stack to AWS.

## Make targets

Provide at least:

```text
make setup
make up
make down
make logs
make health
make test
make bootstrap
make cleanup
make sam-build
make sam-local
```

Targets must be documented and should work on a normal Bash environment. Provide PowerShell equivalents or Windows notes if the repository is being developed on Windows.

## Health-check behavior

`scripts/healthcheck.sh` must verify:

- Docker services are running.
- S3-compatible bucket is reachable.
- API `/health` responds.
- MLflow responds.
- Prometheus responds.
- Grafana responds.
- The active model state is reported as ready or not-ready without exposing secrets.

## Validation

Run and record:

- `docker compose -f infrastructure/compose.yaml config`
- Container image builds.
- Local stack startup.
- Bootstrap script twice to prove idempotency.
- Health check.
- Storage adapter tests.
- Retention cleanup test.
- `sam build` if SAM CLI is installed; otherwise create a clearly documented manual verification step.

## Documentation and evidence

Update:

- Root `README.md` with local startup and shutdown instructions.
- `docs/evidence/E-05-infrastructure/README.md` with commands, results, date, and related requirement IDs.
- The GitHub Issue for local infrastructure with actual evidence links.

At the end, report:

1. Files changed.
2. Commands run and outcomes.
3. Requirements satisfied.
4. Remaining limitations.
5. Exact next command I should run.

---

# Cursor Prompt 02 - Local MLOps Pipeline

Copy everything below into Cursor Agent mode after the local infrastructure baseline exists.

---

Implement the FluentEdge local data, training, evaluation, and model-registry pipeline.

## Scope

Cover:

- FR-DI-001 through FR-DI-007. 
- FR-ML-001 through FR-ML-010, except optional items may remain clearly marked.
- NFR-REL-002.
- NFR-MAINT-001 and NFR-MAINT-002.
- The data and training sections of the design specification.

## Safety and data constraints

- Do not download a large public dataset without asking for approval.
- Use synthetic or tiny fixture audio for automated tests.
- Do not use private student recordings.
- Do not claim pronunciation grading; implement phrase similarity and pass/needs-review classification.
- Prevent target leakage from source validation fields.

## Required modules

Create or adapt:

```text
ml/
├── data/
│   ├── schema.py
│   ├── validate.py
│   ├── preprocess.py
│   └── split.py
├── features/
│   ├── audio.py
│   ├── text.py
│   └── build.py
├── models/
│   ├── train.py
│   ├── predict.py
│   └── registry.py
├── evaluation/
│   ├── metrics.py
│   ├── evaluate.py
│   └── model_card.py
└── pipeline/
    ├── local_pipeline.py
    └── sagemaker_compatible.py
```

Use the existing structure if present.

## Pipeline behavior

Implement stages:

1. Ingest manifest.
2. Validate schema and audio integrity.
3. Normalize text and audio.
4. Produce reproducible speaker-aware splits when speaker IDs exist.
5. Build features.
6. Train at least logistic regression and one tree-based model.
7. Evaluate macro F1, precision, recall, confusion matrix, WER, CER, and latency.
8. Compare candidates.
9. Register the selected model in MLflow with:
   - Git SHA.
   - Dataset manifest hash.
   - Feature schema version.
   - Random seed.
   - Parameters and metrics.
   - Artifact checksum.
   - Approval state.
10. Produce a Markdown model card.

## SageMaker compatibility

Create a thin compatibility layer that:

- Keeps processing, training, and evaluation entry points runnable as normal Python scripts.
- Documents how these scripts map to SageMaker Processing/Training/Pipelines.
- Uses SageMaker Local Mode only if the dependency is practical and tests pass on the current machine.
- Does not make SageMaker SDK installation mandatory for the minimum local demo.
- Never starts managed SageMaker jobs.

## Test fixtures

Create a tiny generated audio fixture set that is safe to commit or generated during tests. Include:

- Valid WAV clip.
- Too-long or boundary clip.
- Corrupt file.
- Duplicate ID case.
- Missing transcript case.
- Prompt-match and prompt-mismatch examples.

## Quality gates

- Macro F1 target: 0.75 for the intended prototype dataset.
- During synthetic fixture testing, document that the metric is functional evidence, not a valid real-world accuracy claim.
- No candidate can receive production/approved status automatically.
- Approval must be an explicit command or documented manual step.

## Commands

Add Make targets or scripts for:

```text
make data-validate
make train
make evaluate
make register
make approve-model MODEL_VERSION=<version>
make pipeline-local
```

## Validation

Run:

- Unit tests for validation and features.
- Pipeline on fixtures.
- Candidate comparison.
- MLflow logging test.
- Model registration test.
- Model-load smoke test.
- Model-card generation.

## Evidence

Create or update:

- `docs/evidence/E-04-data/README.md`
- `docs/evidence/E-06-training-evaluation/README.md`
- Dataset card template.
- Evaluation report.
- Model card.

End with a factual report of commands run, outputs created, requirements covered, and limitations. Do not describe unexecuted steps as completed.

---

# Cursor Prompt 03 - API and Minimal Learner UI

Copy everything below into Cursor Agent mode after a loadable model artifact or fixture model exists.

---

Implement the FluentEdge FastAPI service and a minimal learner interface.

## Scope

Cover:

- FR-API-001 through FR-API-007.
- NFR-PERF-001 and NFR-PERF-002.
- NFR-SEC-002.
- NFR-PRIV-002.
- NFR-OBS-001 and NFR-OBS-002.
- NFR-USAB-001.
- Section 9 of the design specification.

## API requirements

Implement:

- `GET /health`
- `GET /ready`
- `POST /predict`
- `GET /metrics`
- OpenAPI docs in development

`POST /predict` shall:

- Accept an expected phrase and audio upload.
- Enforce media, size, and duration rules.
- Generate a request ID.
- Store input temporarily through the storage adapter.
- Load the approved model through the registry abstraction.
- Return score, label, confidence, feedback categories, model version, request ID, and latency.
- Delete or schedule deletion of temporary audio.
- Never log raw audio, tokens, or full transcripts.

## Error contract

Create deterministic error codes for:

- Missing prompt.
- Unsupported media type.
- Oversized file.
- Decode failure.
- Model not ready.
- Dependency unavailable.
- Internal prediction failure.

All errors must include a request ID and safe user-facing message.

## Metrics

Expose Prometheus metrics for:

- Request count by route and status.
- Error count by error code.
- Request latency histogram.
- Prediction labels.
- Confidence summary.
- Active model version as safe metadata.
- Model-ready state.

Do not use high-cardinality request IDs as metric labels.

## Minimal UI

Implement a simple local web UI using one of these approaches, preferring the lightest fit with the current repository:

1. FastAPI-served HTML/JavaScript.
2. A small React/Vite frontend if one already exists.
3. Streamlit only if it does not complicate deployment.

The UI must include:

- Expected phrase input.
- Audio file upload or browser recording when practical.
- Analyze button.
- Loading state.
- Score, label, confidence, feedback categories, and retry.
- Prototype disclaimer.
- Accessible labels and keyboard operation.

## Tests

Create:

- Contract tests for `/health`, `/ready`, and `/predict`.
- Negative tests for validation failures.
- Log-redaction test.
- Path-traversal test.
- Model-not-ready test.
- Performance smoke test.
- UI smoke test where practical.

## Evidence

Create or update:

- `docs/evidence/E-08-ui-api/README.md`
- OpenAPI JSON or YAML artifact.
- Sample request and response files.
- Screenshot instructions.

At completion, report what actually ran and list any UI actions that still require manual browser testing.

---

# Cursor Prompt 04 - GitHub CLI and GitHub Projects Setup

Copy everything below into Cursor Agent mode after the repository content exists.

---

Configure the FluentEdge GitHub repository and create the GitHub Project that is the approved replacement for Jira. Use GitHub CLI wherever the CLI supports the operation.

## Critical safety rules

1. First run `gh auth status`; do not print tokens.
2. If the `project` scope is missing, instruct me to run `gh auth refresh -s project` and wait for authentication.
3. Do not delete or rename an existing repository, project, label, milestone, issue, branch, or workflow.
4. Do not make the repository public without explicit approval.
5. Do not enable paid features.
6. Create an idempotent script that detects existing resources.
7. Show a dry-run summary before external changes.
8. Require explicit confirmation before running commands that create GitHub resources.

## Variables

Use environment variables and create `templates/github-project-config.example.env` with:

```bash
GITHUB_OWNER="macfindlaichm"
GITHUB_REPO="fluentedge"
GITHUB_PROJECT_TITLE="FluentEdge MLOps"
REPO_VISIBILITY="private"
CURRENT_SPRINT="Sprint 2"
```

Do not assume the owner or repository exists. Resolve `@me` through `gh api user --jq .login` when appropriate.

## Deliverables

Create:

```text
scripts/bootstrap_github.sh
scripts/audit_github_setup.sh
scripts/export_project_evidence.sh
docs/project-management/github-project-setup.md
.github/ISSUE_TEMPLATE/config.yml
.github/ISSUE_TEMPLATE/feature.yml
.github/ISSUE_TEMPLATE/bug.yml
.github/ISSUE_TEMPLATE/documentation.yml
.github/PULL_REQUEST_TEMPLATE.md
```

## Repository configuration

Using `gh` commands, safely create or configure:

- Repository only if it does not exist and only after confirmation.
- Repository description and homepage if provided.
- Labels.
- Milestones.
- Sprint 2 issues.
- GitHub Project.
- Project custom fields.
- Issue-to-project membership.
- Project item field values.

Do not attempt unsupported settings silently. Record manual steps.

## Required labels

Create these labels if absent. Use harmonious colors and keep existing label definitions unless the user approves changes.

| Label | Suggested color | Purpose |
|---|---|---|
| `type:feature` | `1F6FEB` | New capability |
| `type:bug` | `D73A4A` | Defect |
| `type:docs` | `0E8A16` | Documentation |
| `type:test` | `6F42C1` | Testing |
| `area:data` | `2DA44E` | Data work |
| `area:ml` | `8250DF` | ML work |
| `area:api` | `0969DA` | API work |
| `area:infra` | `BF8700` | Infrastructure |
| `area:monitoring` | `FB8F44` | Observability |
| `area:ui` | `D4C5F9` | Interface |
| `priority:p0` | `B60205` | Critical |
| `priority:p1` | `D93F0B` | High |
| `priority:p2` | `FBCA04` | Normal |
| `priority:p3` | `C2E0C6` | Low |
| `status:blocked` | `5319E7` | Blocked work |
| `evidence-required` | `0052CC` | Evidence still needed |
| `sprint:2` | `BFDADC` | Sprint 2 |

## Milestones

Create milestones if absent:

- Sprint 2 - Design and Local Baseline
- Sprint 3 - Data and Model
- Sprint 4 - API, Deployment, and Monitoring
- Final - Demonstration and Evidence

Do not invent due dates. Read dates from repository documentation or require values in the config file.

## GitHub Project

Create a user or organization project titled `FluentEdge MLOps` if absent.

Use:

- `gh project create`
- `gh project field-create`
- `gh project field-list --format json`
- `gh project item-list --format json`
- `gh project item-edit`
- `gh issue create --project`

Always resolve project, field, option, and item IDs from command output. Never hard-code GraphQL IDs.

### Required fields

- Status: use the built-in field and preserve its existing option IDs.
- Priority: P0, P1, P2, P3.
- Sprint: Sprint 1, Sprint 2, Sprint 3, Sprint 4, Final.
- Workstream: Documentation, Data, ML, API, Infrastructure, Testing, Monitoring, UI.
- Requirement IDs: text.
- Target Date: date.
- Evidence: text.
- Risk: Low, Medium, High.

### Status values

Configure or document these statuses:

- Backlog
- Ready
- In Progress
- In Review
- Blocked
- Done

The GitHub CLI may not support creating saved views or modifying every built-in Status option directly. When a configuration cannot be completed safely through supported CLI commands, generate a precise manual checklist with the exact web page and settings to change. Do not falsely report that views or automation were configured.

## Sprint 2 issues

Create issues based on Appendix B of the specification. Each issue body must contain:

```markdown
## Objective

## Scope

## Requirements
- FR-...

## Acceptance Criteria
- [ ] ...

## Evidence Required
- [ ] Commit or pull request
- [ ] Test or workflow run
- [ ] Screenshot or report

## Risks / Blockers

## Completion Notes
```

Assign each issue to the authenticated user, add the Sprint 2 milestone, labels, and GitHub Project.

## Project field values

After issues are added:

- Resolve item IDs with `gh project item-list`.
- Resolve field and option IDs with `gh project field-list`.
- Set Priority, Sprint, Workstream, Requirement IDs, and Risk.
- Set Status to Backlog or Ready.
- Set Evidence to `Pending` initially.
- Set Target Date only when an actual date is provided.

## Repository templates

Issue forms shall require:

- Objective.
- Requirement IDs.
- Acceptance criteria.
- Evidence.
- Risks or blockers.

The pull request template shall require:

- Related issues.
- Requirement IDs.
- Summary.
- Tests run.
- Evidence links.
- Security/privacy review.
- Checklist.

## Audit and evidence export

`audit_github_setup.sh` shall produce a Markdown report that includes:

- Repository URL.
- Project URL and number.
- Labels.
- Milestones.
- Project fields.
- Project items.
- Sprint 2 issue URLs.
- Workflows.
- Manual configuration still required.

`export_project_evidence.sh` shall write `docs/evidence/E-09-github-governance/github-audit.md` without exposing tokens.

## Execution sequence

1. Inspect and plan.
2. Generate scripts and templates.
3. Run shell syntax checks.
4. Show dry-run output.
5. Ask for explicit confirmation.
6. Run GitHub changes.
7. Audit the result.
8. Open the project in a browser with `gh project view <number> --owner <owner> --web` for manual view configuration.

At the end, provide all created URLs and list any manual web-interface steps that remain.

---

# Cursor Prompt 05 - GitHub Actions CI/CD

Copy everything below into Cursor Agent mode after the local commands work.

---

Implement the FluentEdge GitHub Actions CI/CD baseline without creating paid AWS resources.

## Scope

Cover:

- FR-INF-011 and FR-INF-012.
- FR-PM-006.
- NFR-MAINT-001.
- Security, testing, and build requirements from the specification.

## Workflows

Create or update:

```text
.github/workflows/ci.yml
.github/workflows/container.yml
.github/workflows/docs.yml
.github/workflows/manual-local-evidence.yml
.github/dependabot.yml
```

Avoid duplicate workflows if equivalent files already exist.

## `ci.yml`

Run on pull requests and pushes to main:

- Checkout.
- Set up Python.
- Install locked dependencies.
- Format check.
- Lint.
- Type check if configured.
- Unit and integration tests using fixtures.
- Generate JUnit and coverage artifacts.
- Secret scan using an approved action or tool.
- Dependency vulnerability scan.
- `docker compose config` validation.

Use minimum `permissions`. Pin third-party actions to stable major versions or commit SHAs according to repository policy.

## `container.yml`

- Build the FastAPI/inference image.
- Run a container smoke test.
- Do not push to a public registry by default.
- Upload build metadata as an artifact.
- Optional registry push must be disabled unless explicitly configured.

## `docs.yml`

- Validate Markdown formatting or structure.
- Check relative links and required headings.
- Search for unresolved `[INSERT]` placeholders and report them without failing until the final release branch.
- Validate Mermaid blocks syntactically where practical.

## `manual-local-evidence.yml`

Create a manual workflow that:

- Runs tests and generates reports.
- Packages safe evidence artifacts.
- Does not require Docker-in-Docker if the runner cannot support the full local stack.
- Clearly labels which local screenshots must still be captured manually.

## Optional AWS deployment

Do not create a deployment workflow unless I explicitly request it. If a placeholder is included, it must:

- Use GitHub OIDC rather than long-lived access keys.
- Require a protected environment and manual approval.
- Default to disabled.
- Include teardown instructions.

## Branch protection recommendation

Generate `docs/project-management/branch-protection.md` with recommended settings. Do not change repository rules automatically unless I explicitly approve and the current plan supports the feature.

## Validation

Run local equivalents of workflow commands. If `act` is available, it may be used, but do not require it. Validate YAML syntax and explain any checks that can only run on GitHub.

## Evidence

Create `docs/evidence/E-07-deployment-monitoring/ci-cd.md` containing:

- Workflow file links.
- Commands mirrored locally.
- Expected workflow names.
- Fields for Actions run URLs.
- Remaining manual evidence.

End with the exact commit and push steps needed to trigger CI.

---

# Cursor Prompt 06 - Evidence Collection and Documentation Synchronization

Copy everything below into Cursor Agent mode after implementation and GitHub setup are substantially complete.

---

Collect factual evidence for FluentEdge and update the design specification without inventing completion.

## Source of truth

Use:

- Actual repository files.
- Git history.
- GitHub CLI output.
- GitHub Actions run URLs.
- GitHub Issues and Project URLs.
- Local command output.
- MLflow metadata.
- Generated reports.
- User-provided screenshots.

Do not use planned tasks as evidence of completion.

## Tasks

1. Run the repository's audit, tests, health checks, and safe evidence-export commands.
2. Use GitHub CLI to collect:
   - Repository URL.
   - GitHub Project URL.
   - Issue URLs and statuses.
   - Pull request URLs.
   - Commit SHA.
   - Workflow names and latest run URLs.
   - Milestones and labels.
3. Inspect `docs/evidence/` and identify missing screenshots or reports.
4. Generate `docs/evidence/SPRINT2_EVIDENCE_SUMMARY.md`.
5. Update Appendix D of `FluentEdge_Sprint2_Design_and_Requirements_Specification.md` with real links and statuses.
6. Update issue completion comments with evidence links where the CLI can safely do so.
7. Do not close issues whose acceptance criteria are incomplete.
8. Create a manual screenshot checklist for evidence that cannot be captured automatically.

## Required evidence summary format

```markdown
# Sprint 2 Evidence Summary

## Repository
- URL:
- Commit:
- Branch:

## GitHub Project
- URL:
- Project number:
- Manual view configuration completed: Yes/No

## Automated Verification
| Check | Command or workflow | Result | Evidence link |

## Requirements Coverage
| Requirement IDs | Implementation | Test | Evidence |

## Missing Evidence
- [ ] ...

## Known Limitations
- ...
```

## Link quality rules

- Prefer permanent GitHub links containing a commit SHA for source files.
- Link to the exact issue, pull request, Actions run, or artifact page.
- For local screenshots, use repository-relative links.
- Verify that links are not private secrets or local `file://` paths.
- Preserve APA reference links in the specification.

## Final report

At completion, state:

- Which evidence items are complete.
- Which items still require manual screenshots.
- Which issues remain open.
- Whether the document is ready to export to PDF.
- The exact unresolved `[INSERT]` placeholders, if any.
