"""Local end-to-end ML pipeline (FR-INF-005, FR-ML-002)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import mlflow
import pandas as pd

from ml.data.preprocess import preprocess_clip, write_normalized_audio
from ml.data.schema import FEATURE_SCHEMA_VERSION, Manifest
from ml.data.split import assign_splits, manifest_hash
from ml.data.validate import filter_valid_clips, validate_manifest
from ml.evaluation.evaluate import compare_candidates, evaluate_candidate, select_winner
from ml.evaluation.model_card import render_model_card
from ml.features.build import build_feature_frame, feature_matrix
from ml.models.predict import artifact_checksum
from ml.models.registry import configure_mlflow, register_model
from ml.models.train import save_model, train_candidates

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO_ROOT / "tests" / "fixtures" / "synthetic" / "manifest.json"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "runs"


def git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=REPO_ROOT,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def run_pipeline(
    *,
    manifest_path: Path,
    output_dir: Path,
    seed: int = 42,
    tracking_uri: str = "http://localhost:5000",
    register: bool = True,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    base_dir = manifest_path.parent
    manifest = Manifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    manifest.seed = seed

    report = validate_manifest(manifest, base_dir=base_dir)
    (output_dir / "validation_report.json").write_text(
        json.dumps(report.to_dict(), indent=2),
        encoding="utf-8",
    )
    if not report.passed:
        raise RuntimeError("Validation failed; see validation_report.json")

    valid_clips = filter_valid_clips(manifest, report)
    processed = [preprocess_clip(clip, base_dir) for clip in valid_clips]
    normalized_dir = output_dir / "normalized"
    for clip in processed:
        rel = write_normalized_audio(clip, base_dir, normalized_dir)
        clip.audio_uri = rel
    processed = assign_splits(processed, seed=seed)
    m_hash = manifest_hash(processed)
    (output_dir / "clean_manifest.json").write_text(
        Manifest(manifest_version=manifest.manifest_version, seed=seed, clips=processed).model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    feature_frame = build_feature_frame(processed, normalized_dir)
    feature_frame.to_csv(output_dir / "features.csv", index=False)
    (output_dir / "feature_schema.json").write_text(
        json.dumps({"version": FEATURE_SCHEMA_VERSION, "columns": list(feature_frame.columns)}),
        encoding="utf-8",
    )

    train_df = feature_frame[feature_frame["split"] == "train"]
    test_df = feature_frame[feature_frame["split"] == "test"]
    x_train, y_train = feature_matrix(train_df)
    x_test, y_test = feature_matrix(test_df)

    configure_mlflow(tracking_uri)
    run_name = f"fluentedge-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    mlflow.set_experiment("fluentedge-training")
    with mlflow.start_run(run_name=run_name) as run:
        run_id = run.info.run_id
        candidates = train_candidates(x_train, y_train, random_seed=seed)
        evaluations = [
            evaluate_candidate(candidate, x_test, y_test, test_df) for candidate in candidates
        ]
        comparison = compare_candidates(evaluations)
        (output_dir / "evaluation_report.json").write_text(
            json.dumps({"comparison": comparison, "details": [e.__dict__ for e in evaluations]}, indent=2, default=str),
            encoding="utf-8",
        )

        winner = select_winner(evaluations)
        if winner is None:
            raise RuntimeError("No candidate passed the macro F1 quality gate")

        winner_candidate = next(c for c in candidates if c.name == winner.name)
        model_path = output_dir / f"{winner.name}.joblib"
        save_model(winner_candidate.pipeline, model_path)
        checksum = artifact_checksum(model_path)
        production_path = REPO_ROOT / "artifacts" / "production" / "model.joblib"
        production_path.parent.mkdir(parents=True, exist_ok=True)
        save_model(winner_candidate.pipeline, production_path)

        card = render_model_card(
            candidate=winner,
            git_sha=git_sha(),
            manifest_hash=m_hash,
            feature_schema_version=FEATURE_SCHEMA_VERSION,
            random_seed=seed,
            artifact_checksum=checksum,
            dataset_note=(
                "Synthetic fixture dataset for functional pipeline evidence only; "
                "not a real-world accuracy claim."
            ),
        )
        (output_dir / "model_card.md").write_text(card, encoding="utf-8")

        version = ""
        if register:
            version = register_model(
                winner_candidate.pipeline,
                candidate_name=winner.name,
                git_sha=git_sha(),
                manifest_hash=m_hash,
                feature_schema_version=FEATURE_SCHEMA_VERSION,
                random_seed=seed,
                metrics=winner.metrics,
                model_path=model_path,
            )

    return {
        "output_dir": str(output_dir),
        "run_id": run_id,
        "winner": winner.name,
        "model_version": version,
        "macro_f1": winner.metrics["macro_f1"],
        "model_card": str(output_dir / "model_card.md"),
        "validation_passed": report.passed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FluentEdge local ML pipeline")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tracking-uri", default="http://localhost:5000")
    parser.add_argument("--no-register", action="store_true")
    args = parser.parse_args(argv)

    output_dir = args.output_dir or (DEFAULT_OUTPUT / uuid4().hex[:8])
    result = run_pipeline(
        manifest_path=args.manifest,
        output_dir=output_dir,
        seed=args.seed,
        tracking_uri=args.tracking_uri,
        register=not args.no_register,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
