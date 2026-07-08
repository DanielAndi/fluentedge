#!/usr/bin/env python3
"""Explicit model approval command (FR-ML-006)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.models.registry import (  # noqa: E402
    approve_model,
    configure_mlflow,
    get_production_model_uri,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Approve a registered FluentEdge model version")
    parser.add_argument("model_version", help="MLflow model version number")
    parser.add_argument("--tracking-uri", default="http://localhost:5000")
    parser.add_argument("--approver", default="project-owner")
    args = parser.parse_args()

    configure_mlflow(args.tracking_uri)
    approve_model(args.model_version, approver=args.approver)
    uri, version = get_production_model_uri()
    print(f"Approved model version {version}")
    print(f"Artifact URI: {uri}")
    print("Set APPROVED_MODEL_URI and APPROVED_MODEL_VERSION in .env, then restart the API.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
