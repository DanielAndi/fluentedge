# E-01 Architecture Evidence

**Status:** Complete by design-spec reference.

The architecture diagrams are maintained directly in the Sprint 2 design specification as Mermaid source so they remain version-controlled, readable in Markdown, and exportable with the final document.

| Diagram | Location in design specification | Evidence value |
|---|---|---|
| Local runtime architecture | `FluentEdge_Sprint2_Design_and_Requirements_Specification.md`, section 2.4 | Shows learner UI, FastAPI, LocalStack/S3-compatible storage, MLflow, Prometheus, Grafana, GitHub Actions, and GitHub Project governance. |
| AWS target architecture | `FluentEdge_Sprint2_Design_and_Requirements_Specification.md`, section 2.5 | Shows the future AWS mapping for API Gateway, Lambda/container API, S3, SageMaker AI, Model Registry, CloudWatch, and GitHub governance. |
| Data and artifact lineage | `FluentEdge_Sprint2_Design_and_Requirements_Specification.md`, section 5.7 | Shows data flow from fixtures/public dataset through validation, features, model training, approval, API serving, and monitoring evidence. |
| Prediction request sequence | `FluentEdge_Sprint2_Design_and_Requirements_Specification.md`, section 6.2.1 | Shows the runtime `/predict` interaction from browser upload through validation, storage, model scoring, metrics, and response. |
| Evidence review workflow | `FluentEdge_Sprint2_Design_and_Requirements_Specification.md`, section 10.3.1 | Shows requirement-to-issue-to-evidence traceability for final review. |

The prior PNG exports were removed because the specification Mermaid diagrams are the source of truth.

## Commands run

No command is required for E-01. The architecture diagrams are reviewed directly in the design specification Markdown.

Optional validation:

```bash
python3 scripts/validate_docs.py
```

## Results

E-01 is complete by reference to the Mermaid diagrams embedded in the design specification. No separate architecture screenshot is required.
