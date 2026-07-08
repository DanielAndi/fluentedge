#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/audit_github_setup.sh [--config FILE] [--output FILE]

Writes a Markdown audit of the FluentEdge GitHub repository and Project setup.
USAGE
}

CONFIG_FILE=""
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG_FILE="${2:-}"
      shift 2
      ;;
    --output)
      OUTPUT_FILE="${2:-}"
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
REPO_FULL="$GITHUB_OWNER/$GITHUB_REPO"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI is required for audit." >&2
  exit 127
fi

if [[ "$GITHUB_OWNER" == "@me" ]]; then
  GITHUB_OWNER="$(gh api user --jq .login)"
  REPO_FULL="$GITHUB_OWNER/$GITHUB_REPO"
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
REPORT="$TMP_DIR/github-audit.md"

repo_url="$(gh repo view "$REPO_FULL" --json url --jq .url 2>/dev/null || true)"
project_number="$(gh project list --owner "$GITHUB_OWNER" --format json --limit 200 --jq ".projects[] | select(.title == \"$GITHUB_PROJECT_TITLE\") | .number" | head -n 1 || true)"
project_url=""
if [[ -n "$project_number" ]]; then
  project_url="$(gh project view "$project_number" --owner "$GITHUB_OWNER" --format json --jq .url 2>/dev/null || true)"
fi

{
  echo "# GitHub Governance Audit"
  echo
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "## Repository"
  echo
  echo "- Repository: ${repo_url:-Not found}"
  echo "- Owner: $GITHUB_OWNER"
  echo "- Name: $GITHUB_REPO"
  echo
  echo "## Project"
  echo
  echo "- Project title: $GITHUB_PROJECT_TITLE"
  echo "- Project number: ${project_number:-Not found}"
  echo "- Project URL: ${project_url:-Not found}"
  echo
  echo "## Labels"
  echo
  if [[ -n "$repo_url" ]]; then
    gh label list --repo "$REPO_FULL" --limit 500 --json name,color,description --template '{{range .}}{{printf "- `%s` #%s - %s\n" .name .color .description}}{{end}}'
  else
    echo "- Repository not found."
  fi
  echo
  echo "## Milestones"
  echo
  if [[ -n "$repo_url" ]]; then
    gh api "repos/$REPO_FULL/milestones?state=all&per_page=100" --template '{{range .}}{{printf "- %s (%s)\n" .title .state}}{{end}}'
  else
    echo "- Repository not found."
  fi
  echo
  echo "## Project Fields"
  echo
  if [[ -n "$project_number" ]]; then
    gh project field-list "$project_number" --owner "$GITHUB_OWNER" --format json --jq '.fields[] | "- `" + .name + "` (" + .type + ")"'
  else
    echo "- Project not found."
  fi
  echo
  echo "## Project Items"
  echo
  if [[ -n "$project_number" ]]; then
    gh project item-list "$project_number" --owner "$GITHUB_OWNER" --format json --limit 200 --jq '.items[] | "- " + (.content.title // .title // .id)'
  else
    echo "- Project not found."
  fi
  echo
  echo "## Sprint 2 Issue URLs"
  echo
  if [[ -n "$repo_url" ]]; then
    gh issue list --repo "$REPO_FULL" --state all --label "sprint:2" --json title,url --limit 100 --jq '.[] | "- [" + .title + "](" + .url + ")"'
  else
    echo "- Repository not found."
  fi
  echo
  echo "## Workflows"
  echo
  if [[ -n "$repo_url" ]]; then
    gh workflow list --repo "$REPO_FULL" --all || true
  else
    echo "- Repository not found."
  fi
  echo
  echo "## Manual Configuration Still Required"
  echo
  echo "- Confirm Project Status options in the web UI: Backlog, Ready, In Progress, In Review, Blocked, Done."
  echo "- Create saved Project views in the web UI: Sprint Board, Requirements Table, Roadmap, Blocked Work, Evidence Review."
  echo "- Configure branch protection or rulesets manually if required by the account plan."
  echo "- Capture and store screenshots for project fields, board state, and evidence review."
} >"$REPORT"

if [[ -n "$OUTPUT_FILE" ]]; then
  mkdir -p "$(dirname "$OUTPUT_FILE")"
  cp "$REPORT" "$OUTPUT_FILE"
  echo "Wrote audit report: $OUTPUT_FILE"
else
  cat "$REPORT"
fi
