# Sprint 2 Evidence Index

This folder stores the evidence package for the FluentEdge Sprint 2 submission.

## Evidence Mapping

| Evidence ID | What proves it | Path or source |
|---|---|---|
| E-01 Architecture | Mermaid diagrams embedded in the design specification | `FluentEdge_Sprint2_Design_and_Requirements_Specification.md`, sections 2.4, 2.5, 5.7, 6.2.1, and 10.3.1 |
| E-02 Requirements | GitHub Project board plus requirements backlog/table screenshot | `E-09-github-governance/project-board-sprint2.png` and `E-02-requirements/requirements-review.png` |
| E-03 Non-functional | Green CI run plus latency report | `E-07-deployment-monitoring/actions-ci-green.png`, `E-03-non-functional/performance.png`, and `E-03-non-functional/performance-report.json` |
| E-04 Data | Dataset/validation/evaluation evidence | `E-04-data/` |
| E-05 Infrastructure | Health check and local stack evidence | `E-05-infrastructure/` |
| E-06 Training | MLflow and model evaluation evidence | `E-06-training-evaluation/` |
| E-07 Deployment and monitoring | CI/CD, Grafana, Prometheus, rollback evidence | `E-07-deployment-monitoring/` |
| E-08 UI/API | Learner UI, OpenAPI, request/response evidence | `E-08-ui-api/` |
| E-09 Governance | GitHub Project, repository, and governance audit evidence | `E-09-github-governance/project-board-sprint2.png`, `E-09-github-governance/repository-overview.png`, `E-09-github-governance/project-fields.png`, and `E-09-github-governance/github-audit.md` |
| E-10 Final review | Final evidence traceability review | `E-10-final-review/traceability-review.png` and `E-10-final-review/SPRINT2_FINAL_SUBMISSION.md` |

## Screenshot Notes

- The architecture PNG exports were removed. E-01 is satisfied by the Mermaid diagrams embedded in the design specification.
- For E-02, use the GitHub Project board screenshot and requirements backlog/table screenshot.
- For E-03, use the green GitHub Actions CI screenshot plus the local performance report.
- For E-09, use the repository/GitHub Project governance screenshot and audit report.
- For E-10, capture Appendix D of the design specification or issue #9 with final evidence links.

## Commands run

Recommended documentation checks:

```bash
python3 scripts/validate_docs.py
python3 scripts/validate_docs.py --placeholders-only
```

## Results

The evidence package is ready when all required screenshots or documented spec references exist, Appendix D matches the stored evidence, and documentation validation passes.
