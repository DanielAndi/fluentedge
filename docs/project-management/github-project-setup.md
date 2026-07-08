# GitHub Project Setup

This document records the FluentEdge GitHub Issues and GitHub Projects setup that replaces Jira for Sprint 2 governance.

## Safety Rules

- Run `gh auth status` before any GitHub operation.
- If the `project` scope is missing, run `gh auth refresh -s project` before continuing.
- Do not delete or rename existing repositories, projects, labels, milestones, issues, branches, or workflows.
- Do not make the repository public without explicit approval.
- Do not enable paid features.
- Run the bootstrap script in dry-run mode before applying changes.

## Configuration

Copy `templates/github-project-config.example.env` to a local file, update only real values, and source it through the scripts:

```bash
scripts/bootstrap_github.sh --dry-run --config templates/github-project-config.example.env
CONFIRM_GITHUB_CHANGES=yes scripts/bootstrap_github.sh --apply --config templates/github-project-config.example.env
scripts/audit_github_setup.sh --config templates/github-project-config.example.env
scripts/export_project_evidence.sh --config templates/github-project-config.example.env
```

Use `GITHUB_OWNER="@me"` only when the authenticated user should own the repository or Project. The scripts resolve it with `gh api user --jq .login`.

## Bootstrap Behavior

`scripts/bootstrap_github.sh` is idempotent and detects existing resources before creating them.

It can create or configure:

- Private repository, only if absent and confirmed.
- Repository description and homepage, only when environment values are provided.
- Required labels, preserving existing label definitions.
- Required milestones, without invented due dates.
- GitHub Project titled `FluentEdge MLOps`, if absent.
- Project custom fields for Priority, Sprint, Workstream, Requirement IDs, Target Date, Evidence, and Risk.
- Sprint 2 issues from Appendix B.
- Initial project field values after resolving Project, field, option, and item IDs from `gh` command output.

## Manual Web Checklist

Open the Project after bootstrap:

```bash
gh project view <project-number> --owner <owner> --web
```

Then verify or configure:

- Built-in Status options: Backlog, Ready, In Progress, In Review, Blocked, Done.
- Saved view: Sprint Board, grouped by Status and filtered to Sprint 2.
- Saved view: Requirements Table, showing issue, Status, Priority, Workstream, Requirement IDs, Target Date, and Evidence.
- Saved view: Roadmap, using Target Date when real dates are available.
- Saved view: Blocked Work, filtered to Status = Blocked.
- Saved view: Evidence Review, filtered to missing Evidence or Status = In Review.
- Repository branch protection or rulesets, if supported by the account plan.
- Screenshots for Project fields, board state, and evidence review.

## Audit and Evidence

Run:

```bash
scripts/export_project_evidence.sh --config templates/github-project-config.example.env
```

The export writes `docs/evidence/E-09-github-governance/github-audit.md` and includes repository URL, Project URL and number, labels, milestones, fields, items, Sprint 2 issue URLs, workflows, and remaining manual steps. The scripts do not print or store tokens.
