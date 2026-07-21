#!/usr/bin/env python3
"""Generate the Sprint 4 SHA-256 inventory for important project artifacts."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/evidence/E-11-sprint4-validation/artifact-inventory.sha256"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def inventory_paths() -> list[Path]:
    paths = {
        ROOT / "FluentEdge_Sprint4_Prototype_Implementation_Document.md",
        ROOT / "FluentEdge_Sprint4_Prototype_Implementation_Document.pdf",
        ROOT / "artifacts/production/model.joblib",
        ROOT / "docs/data/dataset_card.md",
        ROOT / "docs/evidence/E-06-training-evaluation/mlflow-screenshot.png",
        ROOT / "docs/evidence/E-07-deployment-monitoring/grafana-dashboard.png",
        ROOT / "docs/evidence/E-07-deployment-monitoring/prometheus-targets.png",
        ROOT / "docs/evidence/E-07-deployment-monitoring/actions-ci-sprint4.png",
        ROOT / "docs/evidence/E-08-ui-api/ui-screenshot.png",
        ROOT / "pyproject.toml",
        ROOT / "requirements-dev.lock",
        ROOT / "tests/fixtures/synthetic/manifest.json",
    }
    paths.update((ROOT / "artifacts/runs").glob("*/*"))
    paths.update((ROOT / "docs/evidence/E-11-sprint4-validation").glob("*"))
    return sorted(path for path in paths if path.is_file() and path != OUTPUT)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{digest(path)}  {path.relative_to(ROOT)}" for path in inventory_paths()]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines)} SHA-256 entries to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
