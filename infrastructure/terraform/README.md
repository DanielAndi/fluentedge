# Terraform (optional AWS target profile)

FluentEdge's **required** implementation uses Docker Compose for the local prototype (FR-INF-001, FR-INF-009).

Terraform modules for the AWS target profile (S3, API Gateway, Lambda, SageMaker, CloudWatch) are **not included in Sprint 2 infrastructure** to avoid accidental paid resource creation (NFR-COST-001).

Future work may add:

- `infrastructure/terraform/modules/storage`
- `infrastructure/terraform/modules/api`
- `infrastructure/terraform/environments/demo`

Any AWS deployment must remain behind manual workflow approval (FR-INF-012).
