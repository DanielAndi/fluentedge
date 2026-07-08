# Branch Protection Recommendations

This document recommends GitHub branch protection settings for FluentEdge. **Do not apply these automatically** unless explicitly approved; repository rules depend on account plan and organization policy.

**Requirements:** FR-PM-006, FR-INF-012, NFR-MAINT-001

## Target branch

Protect `main` (or the default integration branch used for Sprint delivery).

## Recommended rules

| Setting | Recommendation | Rationale |
|---------|----------------|-----------|
| Require pull request before merging | Enabled | Prevents direct pushes that bypass review |
| Required approvals | 1 (or instructor/team policy) | Ensures human review before merge |
| Dismiss stale pull request approvals | Enabled | Re-review after new commits |
| Require status checks to pass | Enabled | Enforces CI evidence (FR-PM-006) |
| Required checks | `CI / Lint, test, and security`, `CI / Compose config validation`, `Container / Build and smoke test`, `Docs / Validate documentation` | Matches workflow job names in `.github/workflows/` |
| Require branches to be up to date | Enabled | Avoids merging stale green PRs |
| Require conversation resolution | Enabled (if available) | Keeps review threads closed |
| Restrict who can push | Maintainers only | Reduces accidental direct commits |
| Allow force pushes | Disabled | Protects history and evidence traceability |
| Allow deletions | Disabled | Prevents accidental branch removal |
| Require signed commits | Optional | Enable if course or org policy requires it |

## Environments (optional AWS deployment)

If an AWS deployment workflow is added later (FR-INF-012):

- Create a protected environment (for example `aws-demo`).
- Require manual approval and limit reviewers to maintainers.
- Use GitHub OIDC (`id-token: write`) instead of long-lived AWS access keys.
- Keep deployment disabled by default until explicitly configured.

## Manual configuration steps

1. Open **Settings → Branches** (or **Rules → Rulesets** on newer GitHub UI).
2. Add a rule for `main`.
3. Enable the recommended settings above.
4. After the first CI run on a pull request, select the four required status checks from the list of available checks.
5. Save the rule and verify with a test pull request.

## Evidence

Record the configured rule URL or screenshot in `docs/evidence/E-07-deployment-monitoring/ci-cd.md` under **Remaining manual evidence**.
