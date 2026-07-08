#!/usr/bin/env bash
set -euo pipefail

CONFIG_ARGS=()
if [[ "${1:-}" == "--config" ]]; then
  CONFIG_ARGS=(--config "${2:-}")
fi

OUTPUT_PATH="docs/evidence/E-09-github-governance/github-audit.md"
mkdir -p "$(dirname "$OUTPUT_PATH")"
scripts/audit_github_setup.sh "${CONFIG_ARGS[@]}" --output "$OUTPUT_PATH"
echo "Exported GitHub governance evidence to $OUTPUT_PATH"
