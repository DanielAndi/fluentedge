#!/usr/bin/env bash
# Idempotent LocalStack S3 bucket initialization (FR-INF-002, FR-INF-006)
set -euo pipefail

REGION="${AWS_DEFAULT_REGION:-us-west-2}"
ENDPOINT="http://localhost:4566"

buckets=(
  "fluentedge-uploads"
  "fluentedge-data"
  "fluentedge-artifacts"
)

echo "[init-aws] Initializing S3 buckets in region ${REGION}"

for bucket in "${buckets[@]}"; do
  if awslocal s3api head-bucket --bucket "${bucket}" 2>/dev/null; then
    echo "[init-aws] Bucket already exists: ${bucket}"
  else
    awslocal s3api create-bucket \
      --bucket "${bucket}" \
      --region "${REGION}" \
      --create-bucket-configuration LocationConstraint="${REGION}"
    echo "[init-aws] Created bucket: ${bucket}"
  fi
done

echo "[init-aws] S3 initialization complete"
