#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/bootstrap_github.sh [--dry-run|--apply|--offline-plan] [--config FILE]

Creates or verifies the FluentEdge GitHub repository governance setup.

Safety:
  * Dry-run is the default.
  * --apply requires CONFIRM_GITHUB_CHANGES=yes.
  * Public repositories require ALLOW_PUBLIC_REPO=yes.
  * Existing labels, milestones, issues, projects, and fields are preserved.
  * GitHub GraphQL IDs are resolved from gh output at runtime.
USAGE
}

MODE="dry-run"
CONFIG_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      MODE="dry-run"
      shift
      ;;
    --apply)
      MODE="apply"
      shift
      ;;
    --offline-plan)
      MODE="offline-plan"
      shift
      ;;
    --config)
      CONFIG_FILE="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -n "$CONFIG_FILE" ]]; then
  # shellcheck source=/dev/null
  source "$CONFIG_FILE"
fi

GITHUB_OWNER="${GITHUB_OWNER:-@me}"
GITHUB_REPO="${GITHUB_REPO:-fluentedge}"
GITHUB_PROJECT_TITLE="${GITHUB_PROJECT_TITLE:-FluentEdge MLOps}"
REPO_VISIBILITY="${REPO_VISIBILITY:-private}"
CURRENT_SPRINT="${CURRENT_SPRINT:-Sprint 2}"
REPO_DESCRIPTION="${REPO_DESCRIPTION:-}"
REPO_HOMEPAGE="${REPO_HOMEPAGE:-}"

if [[ "$REPO_VISIBILITY" == "public" && "${ALLOW_PUBLIC_REPO:-}" != "yes" ]]; then
  echo "Refusing to create or configure a public repository without ALLOW_PUBLIC_REPO=yes." >&2
  exit 1
fi

if [[ "$MODE" == "apply" && "${CONFIRM_GITHUB_CHANGES:-}" != "yes" ]]; then
  echo "Refusing to apply GitHub changes without CONFIRM_GITHUB_CHANGES=yes." >&2
  exit 1
fi

LABELS=(
  "type:feature|1F6FEB|New capability"
  "type:bug|D73A4A|Defect"
  "type:docs|0E8A16|Documentation"
  "type:test|6F42C1|Testing"
  "area:data|2DA44E|Data work"
  "area:ml|8250DF|ML work"
  "area:api|0969DA|API work"
  "area:infra|BF8700|Infrastructure"
  "area:monitoring|FB8F44|Observability"
  "area:ui|D4C5F9|Interface"
  "priority:p0|B60205|Critical"
  "priority:p1|D93F0B|High"
  "priority:p2|FBCA04|Normal"
  "priority:p3|C2E0C6|Low"
  "status:blocked|5319E7|Blocked work"
  "evidence-required|0052CC|Evidence still needed"
  "sprint:2|BFDADC|Sprint 2"
)

MILESTONES=(
  "Sprint 2 - Design and Local Baseline"
  "Sprint 3 - Data and Model"
  "Sprint 4 - API, Deployment, and Monitoring"
  "Final - Demonstration and Evidence"
)

PROJECT_FIELDS=(
  "Priority|SINGLE_SELECT|P0,P1,P2,P3"
  "Sprint|SINGLE_SELECT|Sprint 1,Sprint 2,Sprint 3,Sprint 4,Final"
  "Workstream|SINGLE_SELECT|Documentation,Data,ML,API,Infrastructure,Testing,Monitoring,UI"
  "Requirement IDs|TEXT|"
  "Target Date|DATE|"
  "Evidence|TEXT|"
  "Risk|SINGLE_SELECT|Low,Medium,High"
)

ISSUES=(
  "Finalize Sprint 2 design and requirements specification|Complete and review the Sprint 2 design and requirements specification.|Documentation|P1|Medium|Ready|FR-PM-001, FR-PM-005, NFR-MAINT-002|type:docs,evidence-required,sprint:2|TARGET_DATE_DESIGN|Markdown commit, PDF export, review issue"
  "Define data contract and validation rules|Implement the data schema and validation baseline for the prototype dataset.|Data|P1|Medium|Ready|FR-DI-001, FR-DI-003, FR-DI-004, FR-DI-005, FR-DI-006, FR-DI-007|type:feature,area:data,type:test,evidence-required,sprint:2|TARGET_DATE_DATA|Schema, tests, validation output"
  "Build local AWS-compatible infrastructure|Create local Compose, SAM, storage, and health-check infrastructure without paid cloud resources.|Infrastructure|P1|High|Ready|FR-INF-001, FR-INF-002, FR-INF-003, FR-INF-004, FR-INF-007, FR-INF-008, FR-INF-009, NFR-COST-001|type:feature,area:infra,type:test,evidence-required,sprint:2|TARGET_DATE_INFRA|Startup logs and infrastructure files"
  "Create training pipeline skeleton|Create the local ingest-to-evaluation machine-learning pipeline skeleton and artifact flow.|ML|P1|Medium|Ready|FR-INF-005, FR-INF-006, FR-ML-001, FR-ML-002, FR-ML-003, FR-ML-004, FR-ML-005, FR-ML-006, FR-ML-007|type:feature,area:ml,type:test,evidence-required,sprint:2|TARGET_DATE_ML|Pipeline run and artifacts"
  "Create FastAPI service and API contract|Implement health, prediction, error handling, OpenAPI, and learner-facing API contract evidence.|API|P1|Medium|Ready|FR-API-001, FR-API-002, FR-API-003, FR-API-004, FR-API-005, FR-API-006, FR-API-007, NFR-PRIV-002|type:feature,area:api,area:ui,type:test,evidence-required,sprint:2|TARGET_DATE_API|API tests and sample response"
  "Configure GitHub repository and CI|Configure repository governance, labels, templates, workflows, and CI evidence for the class project.|Infrastructure|P1|Medium|Ready|FR-INF-011, FR-INF-012, FR-PM-006, FR-PM-007, FR-PM-008, FR-PM-009, NFR-MAINT-001|type:feature,area:infra,type:test,evidence-required,sprint:2|TARGET_DATE_REPO_CI|Repository settings and Actions run"
  "Configure GitHub Project as Jira replacement|Create the GitHub Project fields, issue membership, status process, milestones, and manual view checklist.|Documentation|P0|Medium|Ready|FR-PM-001, FR-PM-002, FR-PM-003, FR-PM-004, FR-PM-005, FR-PM-007, FR-PM-009|type:feature,priority:p0,evidence-required,sprint:2|TARGET_DATE_PROJECT|Project screenshot and link"
  "Create monitoring and rollback baseline|Create Prometheus, Grafana, health, and rollback baseline evidence for local operations.|Monitoring|P2|Medium|Backlog|FR-INF-008, FR-ML-006, FR-ML-007, NFR-REL-001, NFR-REL-002, NFR-OBS-001, NFR-OBS-002|type:feature,area:monitoring,area:ml,type:test,evidence-required,sprint:2|TARGET_DATE_MONITORING|Dashboard and rollback test"
  "Synchronize Sprint 2 evidence|Link issues, commits, reports, screenshots, and Appendix D evidence without inventing completion.|Documentation|P1|Medium|Backlog|FR-PM-001, FR-PM-005, FR-PM-006, NFR-MAINT-002|type:docs,evidence-required,sprint:2|TARGET_DATE_EVIDENCE|Completed Appendix D"
)

print_plan() {
  cat <<PLAN
# FluentEdge GitHub Bootstrap Summary

Mode: $MODE
Owner: $GITHUB_OWNER
Repository: $GITHUB_REPO
Project title: $GITHUB_PROJECT_TITLE
Repository visibility: $REPO_VISIBILITY
Current sprint: $CURRENT_SPRINT

Planned labels: ${#LABELS[@]}
Planned milestones: ${#MILESTONES[@]}
Planned project fields: ${#PROJECT_FIELDS[@]} custom fields plus built-in Status
Planned Sprint 2 issues: ${#ISSUES[@]}

Manual configuration that may remain:
- Confirm or add built-in Status options: Backlog, Ready, In Progress, In Review, Blocked, Done.
- Create saved Project views: Sprint Board, Requirements Table, Roadmap, Blocked Work, Evidence Review.
- Configure any repository branch protection rules that your account/plan supports.
- Capture a Project screenshot for evidence after the board is configured.
PLAN
}

if [[ "$MODE" == "offline-plan" ]]; then
  print_plan
  exit 0
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI is required. Install gh, then run: gh auth status" >&2
  exit 127
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required for JSON parsing." >&2
  exit 127
fi

echo "# gh auth status"
AUTH_STATUS="$(gh auth status 2>&1 || true)"
printf '%s\n' "$AUTH_STATUS"
if ! grep -Eq "Token scopes:.*project|Token scopes:.*'project'|project" <<<"$AUTH_STATUS"; then
  echo "The GitHub CLI token appears to be missing the project scope." >&2
  echo "Run: gh auth refresh -s project" >&2
  exit 1
fi

if [[ "$GITHUB_OWNER" == "@me" ]]; then
  GITHUB_OWNER="$(gh api user --jq .login)"
fi

REPO_FULL="$GITHUB_OWNER/$GITHUB_REPO"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

run_or_echo() {
  if [[ "$MODE" == "apply" ]]; then
    "$@"
  else
    printf 'DRY RUN:'
    printf ' %q' "$@"
    printf '\n'
  fi
}

repo_exists() {
  gh repo view "$REPO_FULL" --json url >/dev/null 2>&1
}

label_exists() {
  local name="$1"
  gh label list --repo "$REPO_FULL" --limit 500 --json name --jq '.[].name' | grep -Fxq "$name"
}

milestone_exists() {
  local title="$1"
  gh api "repos/$REPO_FULL/milestones?state=all&per_page=100" --jq '.[].title' | grep -Fxq "$title"
}

issue_number_by_title() {
  local title="$1"
  gh issue list --repo "$REPO_FULL" --state all --search "$title in:title" --json number,title --jq ".[] | select(.title == \"$title\") | .number" | head -n 1
}

project_number_by_title() {
  gh project list --owner "$GITHUB_OWNER" --format json --limit 200 --jq ".projects[] | select(.title == \"$GITHUB_PROJECT_TITLE\") | .number" | head -n 1
}

field_id() {
  local fields_file="$1"
  local field_name="$2"
  python3 - "$fields_file" "$field_name" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
for field in data.get("fields", []):
    if field.get("name") == sys.argv[2]:
        print(field.get("id", ""))
        break
PY
}

option_id() {
  local fields_file="$1"
  local field_name="$2"
  local option_name="$3"
  python3 - "$fields_file" "$field_name" "$option_name" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
for field in data.get("fields", []):
    if field.get("name") == sys.argv[2]:
        for option in field.get("options", []):
            if option.get("name") == sys.argv[3]:
                print(option.get("id", ""))
                raise SystemExit
PY
}

item_id_for_title() {
  local items_file="$1"
  local title="$2"
  python3 - "$items_file" "$title" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
for item in data.get("items", []):
    content = item.get("content") or {}
    if content.get("title") == sys.argv[2]:
        print(item.get("id", ""))
        break
PY
}

create_issue_body() {
  local path="$1"
  local title="$2"
  local objective="$3"
  local reqs="$4"
  local evidence="$5"
  cat >"$path" <<BODY
## Objective

$objective

## Scope

- Complete the Sprint 2 work item: $title.
- Keep evidence linked to GitHub Issues, pull requests, commits, test output, screenshots, or reports.
- Preserve local-first execution and avoid paid cloud resources unless separately approved.

## Requirements
$(printf '%s\n' "$reqs" | tr ',' '\n' | sed 's/^ */- /')

## Acceptance Criteria
- [ ] Required scope is implemented or explicitly documented as deferred.
- [ ] Relevant tests, checks, or review steps pass.
- [ ] Requirement IDs are linked in code, documentation, pull request, or evidence.
- [ ] Evidence is attached or linked from the issue and project fields.

## Evidence Required
- [ ] Commit or pull request
- [ ] Test or workflow run
- [ ] Screenshot or report

## Risks / Blockers

- Evidence is pending until implementation and verification links are attached.

## Completion Notes

Pending.

<!-- Appendix B expected evidence: $evidence -->
BODY
}

print_plan

REPO_AVAILABLE=false
if repo_exists; then
  echo "Repository exists: $REPO_FULL"
  REPO_AVAILABLE=true
else
  echo "Repository does not exist: $REPO_FULL"
  if [[ "$REPO_VISIBILITY" == "private" ]]; then
    run_or_echo gh repo create "$REPO_FULL" --private
  else
    run_or_echo gh repo create "$REPO_FULL" --public
  fi
  if [[ "$MODE" == "apply" ]]; then
    REPO_AVAILABLE=true
  fi
fi

if [[ -n "$REPO_DESCRIPTION" ]]; then
  run_or_echo gh repo edit "$REPO_FULL" --description "$REPO_DESCRIPTION"
fi
if [[ -n "$REPO_HOMEPAGE" ]]; then
  run_or_echo gh repo edit "$REPO_FULL" --homepage "$REPO_HOMEPAGE"
fi

for label in "${LABELS[@]}"; do
  IFS='|' read -r name color description <<<"$label"
  if [[ "$REPO_AVAILABLE" == "true" ]] && label_exists "$name"; then
    echo "Label exists, preserving definition: $name"
  else
    run_or_echo gh label create "$name" --repo "$REPO_FULL" --color "$color" --description "$description"
  fi
done

for milestone in "${MILESTONES[@]}"; do
  if [[ "$REPO_AVAILABLE" == "true" ]] && milestone_exists "$milestone"; then
    echo "Milestone exists: $milestone"
  else
    run_or_echo gh api "repos/$REPO_FULL/milestones" -f title="$milestone"
  fi
done

PROJECT_NUMBER="$(project_number_by_title || true)"
if [[ -z "$PROJECT_NUMBER" ]]; then
  PROJECT_OUTPUT="$TMP_DIR/project-create.json"
  if [[ "$MODE" == "apply" ]]; then
    gh project create --owner "$GITHUB_OWNER" --title "$GITHUB_PROJECT_TITLE" --format json >"$PROJECT_OUTPUT"
    PROJECT_NUMBER="$(python3 - "$PROJECT_OUTPUT" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(data.get("number", ""))
PY
)"
  else
    run_or_echo gh project create --owner "$GITHUB_OWNER" --title "$GITHUB_PROJECT_TITLE"
    PROJECT_NUMBER="DRY_RUN_PROJECT_NUMBER"
  fi
else
  echo "Project exists: $GITHUB_PROJECT_TITLE (#$PROJECT_NUMBER)"
fi

if [[ "$MODE" == "apply" || "$PROJECT_NUMBER" != "DRY_RUN_PROJECT_NUMBER" ]]; then
  FIELDS_FILE="$TMP_DIR/project-fields.json"
  gh project field-list "$PROJECT_NUMBER" --owner "$GITHUB_OWNER" --format json >"$FIELDS_FILE"

  for field in "${PROJECT_FIELDS[@]}"; do
    IFS='|' read -r name data_type options <<<"$field"
    if [[ -n "$(field_id "$FIELDS_FILE" "$name")" ]]; then
      echo "Project field exists: $name"
    else
      if [[ "$data_type" == "SINGLE_SELECT" ]]; then
        run_or_echo gh project field-create "$PROJECT_NUMBER" --owner "$GITHUB_OWNER" --name "$name" --data-type "$data_type" --single-select-options "$options"
      else
        run_or_echo gh project field-create "$PROJECT_NUMBER" --owner "$GITHUB_OWNER" --name "$name" --data-type "$data_type"
      fi
    fi
  done
else
  for field in "${PROJECT_FIELDS[@]}"; do
    IFS='|' read -r name data_type options <<<"$field"
    if [[ "$data_type" == "SINGLE_SELECT" ]]; then
      run_or_echo gh project field-create "<project-number>" --owner "$GITHUB_OWNER" --name "$name" --data-type "$data_type" --single-select-options "$options"
    else
      run_or_echo gh project field-create "<project-number>" --owner "$GITHUB_OWNER" --name "$name" --data-type "$data_type"
    fi
  done
fi

for issue in "${ISSUES[@]}"; do
  IFS='|' read -r title objective workstream priority risk status reqs labels target_var evidence <<<"$issue"
  if [[ "$REPO_AVAILABLE" == "true" && -n "$(issue_number_by_title "$title" || true)" ]]; then
    echo "Issue exists, preserving: $title"
    continue
  fi
  BODY_FILE="$TMP_DIR/issue-${title//[^A-Za-z0-9]/-}.md"
  create_issue_body "$BODY_FILE" "$title" "$objective" "$reqs" "$evidence"
  target_date="${!target_var:-}"
  label_args=()
  IFS=',' read -ra label_names <<<"$labels"
  for label_name in "${label_names[@]}"; do
    label_args+=(--label "$label_name")
  done
  run_or_echo gh issue create \
    --repo "$REPO_FULL" \
    --title "$title" \
    --body-file "$BODY_FILE" \
    --assignee "@me" \
    --milestone "Sprint 2 - Design and Local Baseline" \
    --project "$GITHUB_PROJECT_TITLE" \
    "${label_args[@]}"
  if [[ -n "$target_date" ]]; then
    echo "Target date for '$title' will be set to $target_date after project item resolution."
  fi
done

if [[ "$MODE" == "apply" ]]; then
  PROJECT_VIEW_FILE="$TMP_DIR/project-view.json"
  FIELDS_FILE="$TMP_DIR/project-fields-after.json"
  ITEMS_FILE="$TMP_DIR/project-items.json"
  gh project view "$PROJECT_NUMBER" --owner "$GITHUB_OWNER" --format json >"$PROJECT_VIEW_FILE"
  gh project field-list "$PROJECT_NUMBER" --owner "$GITHUB_OWNER" --format json >"$FIELDS_FILE"
  gh project item-list "$PROJECT_NUMBER" --owner "$GITHUB_OWNER" --format json --limit 200 >"$ITEMS_FILE"
  PROJECT_ID="$(python3 - "$PROJECT_VIEW_FILE" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(data.get("id", ""))
PY
)"

  for issue in "${ISSUES[@]}"; do
    IFS='|' read -r title _objective workstream priority risk status reqs _labels target_var _evidence <<<"$issue"
    item_id="$(item_id_for_title "$ITEMS_FILE" "$title")"
    if [[ -z "$item_id" ]]; then
      echo "Could not resolve project item for issue: $title" >&2
      continue
    fi

    for field_value in "Priority:$priority" "Sprint:$CURRENT_SPRINT" "Workstream:$workstream" "Risk:$risk" "Status:$status"; do
      field_name="${field_value%%:*}"
      option_name="${field_value#*:}"
      fid="$(field_id "$FIELDS_FILE" "$field_name")"
      oid="$(option_id "$FIELDS_FILE" "$field_name" "$option_name")"
      if [[ -n "$fid" && -n "$oid" ]]; then
        gh project item-edit --id "$item_id" --project-id "$PROJECT_ID" --field-id "$fid" --single-select-option-id "$oid"
      else
        echo "Manual field update needed for '$title': $field_name = $option_name"
      fi
    done

    for field_text in "Requirement IDs:$reqs" "Evidence:Pending"; do
      field_name="${field_text%%:*}"
      text_value="${field_text#*:}"
      fid="$(field_id "$FIELDS_FILE" "$field_name")"
      if [[ -n "$fid" ]]; then
        gh project item-edit --id "$item_id" --project-id "$PROJECT_ID" --field-id "$fid" --text "$text_value"
      fi
    done

    target_date="${!target_var:-}"
    if [[ -n "$target_date" ]]; then
      fid="$(field_id "$FIELDS_FILE" "Target Date")"
      if [[ -n "$fid" ]]; then
        gh project item-edit --id "$item_id" --project-id "$PROJECT_ID" --field-id "$fid" --date "$target_date"
      fi
    fi
  done
else
  echo "Dry run complete. Re-run with CONFIRM_GITHUB_CHANGES=yes scripts/bootstrap_github.sh --apply after reviewing the summary."
fi
