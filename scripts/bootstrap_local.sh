#!/usr/bin/env bash
# Bootstrap local FluentEdge resources (FR-INF-001, FR-INF-006)
# Safe to rerun: detects existing buckets and directories.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env
fi

AWS_REGION="${AWS_REGION:-us-west-2}"
S3_ENDPOINT_URL="${S3_ENDPOINT_URL:-http://localhost:4566}"
AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"
FILESYSTEM_STORAGE_ROOT="${FILESYSTEM_STORAGE_ROOT:-.local-storage}"

BUCKETS=(
  "${S3_UPLOAD_BUCKET:-fluentedge-uploads}"
  "${S3_DATA_BUCKET:-fluentedge-data}"
  "${S3_ARTIFACTS_BUCKET:-fluentedge-artifacts}"
)

export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_DEFAULT_REGION="${AWS_REGION}"

echo "[bootstrap] Ensuring filesystem storage root: ${FILESYSTEM_STORAGE_ROOT}"
mkdir -p "${FILESYSTEM_STORAGE_ROOT}"
for bucket in "${BUCKETS[@]}"; do
  mkdir -p "${FILESYSTEM_STORAGE_ROOT}/${bucket}"
done

echo "[bootstrap] Ensuring S3 buckets at ${S3_ENDPOINT_URL}"
for bucket in "${BUCKETS[@]}"; do
  if aws --endpoint-url="${S3_ENDPOINT_URL}" s3api head-bucket --bucket "${bucket}" 2>/dev/null; then
    echo "[bootstrap] Bucket exists: ${bucket}"
  else
    aws --endpoint-url="${S3_ENDPOINT_URL}" s3api create-bucket \
      --bucket "${bucket}" \
      --region "${AWS_REGION}" \
      --create-bucket-configuration LocationConstraint="${AWS_REGION}" \
      2>/dev/null || aws --endpoint-url="${S3_ENDPOINT_URL}" s3 mb "s3://${bucket}" 2>/dev/null || true
    if aws --endpoint-url="${S3_ENDPOINT_URL}" s3api head-bucket --bucket "${bucket}" 2>/dev/null; then
      echo "[bootstrap] Created bucket: ${bucket}"
    else
      echo "[bootstrap] Warning: could not verify bucket ${bucket} (LocalStack may still be starting)"
    fi
  fi
done

echo "[bootstrap] Creating evidence directories"
mkdir -p docs/evidence/E-05-infrastructure

echo "[bootstrap] Complete"
