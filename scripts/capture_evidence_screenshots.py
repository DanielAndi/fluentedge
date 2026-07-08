#!/usr/bin/env python3
"""Capture local evidence screenshots for Sprint 2 submission."""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "evidence"
WAV = ROOT / "tests" / "fixtures" / "synthetic" / "clip_000.wav"


def capture() -> None:
    targets = {
        "E-08-ui-api/ui-screenshot.png": _capture_ui,
        "E-06-training-evaluation/mlflow-screenshot.png": _capture_mlflow,
        "E-07-deployment-monitoring/grafana-dashboard.png": _capture_grafana,
        "E-07-deployment-monitoring/prometheus-targets.png": _capture_prometheus,
        "E-02-requirements/requirements-review.png": _capture_requirements,
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()
        for rel, fn in targets.items():
            out = EVIDENCE / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            fn(page, out)
            print(f"captured {out}")
        browser.close()


def _capture_ui(page, out: Path) -> None:
    page.goto("http://localhost:8000/", wait_until="networkidle")
    page.get_by_label("Expected phrase").fill("the quick brown fox")
    page.get_by_label("Audio file (WAV, FLAC, MP3, M4A)").set_input_files(str(WAV))
    page.get_by_role("button", name="Analyze").click()
    page.wait_for_timeout(20000)
    page.screenshot(path=str(out), full_page=True)


def _capture_mlflow(page, out: Path) -> None:
    page.goto("http://localhost:5000/", wait_until="networkidle")
    page.wait_for_timeout(2000)
    page.screenshot(path=str(out), full_page=True)


def _capture_grafana(page, out: Path) -> None:
    page.goto("http://localhost:3000/", wait_until="networkidle")
    page.wait_for_timeout(1500)
    page.goto(
        "http://localhost:3000/d/fluentedge-operations/fluentedge-operations",
        wait_until="networkidle",
    )
    page.wait_for_timeout(3000)
    page.screenshot(path=str(out), full_page=True)


def _capture_prometheus(page, out: Path) -> None:
    page.goto("http://localhost:9090/targets", wait_until="networkidle")
    page.wait_for_timeout(2000)
    page.screenshot(path=str(out), full_page=True)


def _capture_requirements(page, out: Path) -> None:
    page.goto(
        "https://github.com/DanielAndi/fluentedge/issues/1",
        wait_until="networkidle",
    )
    page.wait_for_timeout(3000)
    page.screenshot(path=str(out), full_page=True)


if __name__ == "__main__":
    try:
        capture()
    except Exception as exc:
        print(f"screenshot capture failed: {exc}", file=sys.stderr)
        sys.exit(1)
