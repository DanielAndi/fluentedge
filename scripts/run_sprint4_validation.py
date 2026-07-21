#!/usr/bin/env python3
"""Run the repeatable local Sprint 4 reliability and performance checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs/evidence/E-11-sprint4-validation"
DEFAULT_MODEL = REPO_ROOT / "artifacts/production/model.joblib"
DEFAULT_AUDIO = REPO_ROOT / "tests/fixtures/synthetic/clip_000.wav"
PREDICT_TARGET_MS = 2_000.0


class DependencyHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')

    def log_message(self, format: str, *args: object) -> None:
        return


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def percentile(values: list[float], percent: float) -> float:
    ordered = sorted(values)
    index = max(0, math.ceil(percent * len(ordered)) - 1)
    return round(ordered[index], 3)


def summarize(values: list[float]) -> dict[str, float]:
    return {
        "min_ms": round(min(values), 3),
        "p50_ms": percentile(values, 0.50),
        "p95_ms": percentile(values, 0.95),
        "max_ms": round(max(values), 3),
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@contextmanager
def dependency_server():
    port = free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), DependencyHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@contextmanager
def api_server(
    *,
    cycle: int,
    model_path: Path,
    storage_root: Path,
    dependency_url: str,
    output_dir: Path,
):
    port = free_port()
    base_url = f"http://127.0.0.1:{port}"
    log_path = output_dir / f"startup-cycle-{cycle}.log"
    env = os.environ.copy()
    env.update(
        {
            "APPROVED_MODEL_URI": str(model_path),
            "APPROVED_MODEL_VERSION": "sprint4-local-approved",
            "FILESYSTEM_STORAGE_ROOT": str(storage_root),
            "MLFLOW_TRACKING_URI": dependency_url,
            "PYTHONUNBUFFERED": "1",
            "STORAGE_BACKEND": "filesystem",
        }
    )
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "api.app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=REPO_ROOT,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(
                        f"API startup cycle {cycle} exited with {process.returncode}"
                    )
                try:
                    if httpx.get(f"{base_url}/api", timeout=1).status_code == 200:
                        break
                except httpx.HTTPError:
                    time.sleep(0.2)
            else:
                raise TimeoutError(f"API startup cycle {cycle} did not become reachable")
            yield base_url, log_path
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


def timed_get(url: str) -> tuple[int, float, dict]:
    started = time.perf_counter()
    response = httpx.get(url, timeout=10)
    elapsed_ms = (time.perf_counter() - started) * 1_000
    return response.status_code, elapsed_ms, response.json()


def timed_predict(url: str, audio: bytes) -> tuple[int, float, dict]:
    started = time.perf_counter()
    response = httpx.post(
        url,
        data={"expected_phrase": "the quick brown fox"},
        files={"file": ("clip_000.wav", audio, "audio/wav")},
        timeout=30,
    )
    elapsed_ms = (time.perf_counter() - started) * 1_000
    return response.status_code, elapsed_ms, response.json()


def run_rollback_exercise(model_path: Path, work_dir: Path) -> dict:
    approved_sha = sha256(model_path)
    active_path = work_dir / "active-model.joblib"
    shutil.copy2(model_path, active_path)
    active_path.write_bytes(active_path.read_bytes() + b"injected-candidate-corruption")
    bad_sha = sha256(active_path)
    mismatch_detected = bad_sha != approved_sha

    staged_path = work_dir / "rollback-model.tmp"
    shutil.copy2(model_path, staged_path)
    staged_sha = sha256(staged_path)
    if staged_sha != approved_sha:
        raise RuntimeError("Rollback source failed SHA-256 verification")
    staged_path.replace(active_path)
    restored_sha = sha256(active_path)

    from ml.models.predict import load_pipeline

    loaded = load_pipeline(active_path)
    passed = mismatch_detected and restored_sha == approved_sha and hasattr(loaded, "predict")
    return {
        "passed": passed,
        "algorithm": "SHA-256",
        "approved_sha256": approved_sha,
        "rejected_candidate_sha256": bad_sha,
        "mismatch_detected": mismatch_detected,
        "restored_sha256": restored_sha,
        "restored_model_loadable": hasattr(loaded, "predict"),
    }


def run_validation(output_dir: Path, request_count: int) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    if request_count < 30:
        raise ValueError("request_count must be at least 30")
    if not DEFAULT_MODEL.is_file() or not DEFAULT_AUDIO.is_file():
        raise FileNotFoundError("The approved model and synthetic audio fixture are required")

    audio = DEFAULT_AUDIO.read_bytes()
    result: dict = {
        "generated_at": datetime.now(UTC).isoformat(),
        "python_version": sys.version.split()[0],
        "model_path": str(DEFAULT_MODEL.relative_to(REPO_ROOT)),
        "audio_fixture": str(DEFAULT_AUDIO.relative_to(REPO_ROOT)),
        "startup_cycles": [],
    }

    with tempfile.TemporaryDirectory(prefix="fluentedge-sprint4-") as tmp:
        work_dir = Path(tmp)
        with dependency_server() as dependency_url:
            for cycle in (1, 2):
                storage_root = work_dir / f"storage-cycle-{cycle}"
                with api_server(
                    cycle=cycle,
                    model_path=DEFAULT_MODEL,
                    storage_root=storage_root,
                    dependency_url=dependency_url,
                    output_dir=output_dir,
                ) as (base_url, log_path):
                    health_status, _, health_body = timed_get(f"{base_url}/health")
                    ready_status, _, ready_body = timed_get(f"{base_url}/ready")
                    cycle_passed = (
                        health_status == 200
                        and health_body["status"] == "ok"
                        and ready_status == 200
                        and ready_body["model_ready"] is True
                    )
                    result["startup_cycles"].append(
                        {
                            "cycle": cycle,
                            "passed": cycle_passed,
                            "health_status": health_status,
                            "health_body": health_body,
                            "ready_status": ready_status,
                            "ready_body": ready_body,
                            "log": str(log_path.relative_to(REPO_ROOT)),
                        }
                    )

                    if cycle != 1:
                        continue

                    warm_status, _, warm_body = timed_predict(f"{base_url}/predict", audio)
                    if warm_status != 200:
                        raise RuntimeError(f"Warm-up prediction failed: {warm_body}")

                    predictions = [
                        timed_predict(f"{base_url}/predict", audio) for _ in range(request_count)
                    ]
                    predict_times = [item[1] for item in predictions]
                    predict_ids = [item[2].get("request_id") for item in predictions]
                    predict_summary = summarize(predict_times)
                    result["predict_performance"] = {
                        "requests": request_count,
                        **predict_summary,
                        "target_p95_ms": PREDICT_TARGET_MS,
                        "all_status_200": all(item[0] == 200 for item in predictions),
                        "unique_request_ids": len(set(predict_ids)) == request_count,
                        "passed": (
                            all(item[0] == 200 for item in predictions)
                            and predict_summary["p95_ms"] <= PREDICT_TARGET_MS
                        ),
                    }

                    health_results = [timed_get(f"{base_url}/health") for _ in range(request_count)]
                    health_times = [item[1] for item in health_results]
                    result["health_performance"] = {
                        "requests": request_count,
                        **summarize(health_times),
                        "all_status_200": all(item[0] == 200 for item in health_results),
                        "all_service_status_ok": all(
                            item[2].get("status") == "ok" for item in health_results
                        ),
                    }

                    with ThreadPoolExecutor(max_workers=5) as executor:
                        futures = [
                            executor.submit(timed_predict, f"{base_url}/predict", audio)
                            for _ in range(5)
                        ]
                        concurrent = [future.result() for future in futures]
                    concurrent_ids = [item[2].get("request_id") for item in concurrent]
                    leftover_files = [path for path in storage_root.rglob("*") if path.is_file()]
                    result["concurrency"] = {
                        "simultaneous_requests": 5,
                        "all_status_200": all(item[0] == 200 for item in concurrent),
                        "unique_request_ids": len(set(concurrent_ids)) == 5,
                        "leftover_upload_files": len(leftover_files),
                        "passed": (
                            all(item[0] == 200 for item in concurrent)
                            and len(set(concurrent_ids)) == 5
                            and not leftover_files
                        ),
                    }

        result["rollback"] = run_rollback_exercise(DEFAULT_MODEL, work_dir)

    result["passed"] = all(
        [
            all(cycle["passed"] for cycle in result["startup_cycles"]),
            result["predict_performance"]["passed"],
            result["health_performance"]["all_status_200"],
            result["health_performance"]["all_service_status_ok"],
            result["concurrency"]["passed"],
            result["rollback"]["passed"],
        ]
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--requests", type=int, default=30)
    args = parser.parse_args()

    result = run_validation(args.output_dir.resolve(), args.requests)
    report_path = args.output_dir.resolve() / "validation-report.json"
    report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Wrote {report_path}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
