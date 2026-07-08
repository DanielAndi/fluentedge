#!/usr/bin/env bash
# FluentEdge stack health verification (FR-INF-008)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env
fi

API_URL="${API_URL:-http://localhost:8000}"
MLFLOW_URL="${MLFLOW_TRACKING_URI:-http://localhost:5000}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
S3_ENDPOINT_URL="${S3_ENDPOINT_URL:-http://localhost:4566}"
S3_UPLOAD_BUCKET="${S3_UPLOAD_BUCKET:-fluentedge-uploads}"
COMPOSE_FILE="${COMPOSE_FILE:-infrastructure/compose.yaml}"

PASS=0
FAIL=0

check() {
  local name="$1"
  shift
  if "$@"; then
    echo "[health] PASS: ${name}"
    PASS=$((PASS + 1))
  else
    echo "[health] FAIL: ${name}" >&2
    FAIL=$((FAIL + 1))
  fi
}

check_docker_services() {
  docker compose -f "${COMPOSE_FILE}" ps --status running --format '{{.Service}}' | grep -q .
}

check_s3_bucket() {
  AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}" \
  AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}" \
  AWS_DEFAULT_REGION="${AWS_REGION:-us-west-2}" \
    aws --endpoint-url="${S3_ENDPOINT_URL}" s3api head-bucket --bucket "${S3_UPLOAD_BUCKET}" >/dev/null 2>&1
}

check_api_health() {
  local response
  response="$(curl -sf "${API_URL}/health")"
  echo "${response}" | grep -q '"status"'
  echo "${response}" | grep -q '"model_ready"'
  echo ""
  echo "--- API /health summary ---"
  echo "${response}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('status:', data.get('status'))
print('model_ready:', data.get('model_ready'))
deps = data.get('dependencies', {})
for name, info in deps.items():
    print(f'  {name}:', info.get('status'))
"
}

check_mlflow() {
  curl -sf "${MLFLOW_URL}/health" >/dev/null
}

check_prometheus() {
  curl -sf "${PROMETHEUS_URL}/-/healthy" >/dev/null
}

check_grafana() {
  curl -sf "${GRAFANA_URL}/api/health" >/dev/null
}

echo "[health] FluentEdge health check"
echo "[health] Compose file: ${COMPOSE_FILE}"

check "Docker services running" check_docker_services
check "S3 upload bucket reachable" check_s3_bucket
check "API /health responds" check_api_health
check "MLflow responds" check_mlflow
check "Prometheus responds" check_prometheus
check "Grafana responds" check_grafana

echo ""
echo "[health] Results: ${PASS} passed, ${FAIL} failed"

if [[ "${FAIL}" -gt 0 ]]; then
  exit 1
fi

echo "[health] All checks passed"
