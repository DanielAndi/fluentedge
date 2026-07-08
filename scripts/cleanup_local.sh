#!/usr/bin/env bash
# Stop FluentEdge local stack and optional cleanup (§8.7, NFR-COST-002)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

COMPOSE_FILE="${COMPOSE_FILE:-infrastructure/compose.yaml}"
REMOVE_VOLUMES="${REMOVE_VOLUMES:-0}"

echo "[cleanup] Stopping containers"
docker compose -f "${COMPOSE_FILE}" down

if [[ "${REMOVE_VOLUMES}" == "1" ]]; then
  echo "[cleanup] Removing named volumes (preserves approved artifacts only if backed up)"
  docker compose -f "${COMPOSE_FILE}" down -v
fi

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env
fi

echo "[cleanup] Running upload retention cleanup"
python3 scripts/verify_retention.py --cleanup || true

echo "[cleanup] Complete. Approved model artifacts in MLflow volume are preserved unless REMOVE_VOLUMES=1."
