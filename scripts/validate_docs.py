#!/usr/bin/env python3
"""Validate Markdown documentation for CI (FR-PM-006, NFR-MAINT-001)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_SUFFIX = {".md", ".markdown"}
MERMAID_OPEN = re.compile(r"^```mermaid\s*$", re.MULTILINE)
MERMAID_TYPES = (
    "graph",
    "flowchart",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "erDiagram",
    "journey",
    "gantt",
    "pie",
    "gitGraph",
    "mindmap",
    "timeline",
    "C4Context",
)
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^#\s+\S", re.MULTILINE)
EVIDENCE_REQUIRED_SECTIONS = ("## Commands run", "## Results")


def iter_markdown_files() -> list[Path]:
    skip_dirs = {".git", ".venv", "venv", "node_modules", ".aws-sam", "artifacts", "mlruns"}
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in MARKDOWN_SUFFIX:
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def should_require_heading(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if rel.parts and rel.parts[0] == ".github":
        return False
    if (
        len(rel.parts) >= 2
        and rel.parts[:2] == ("docs", "evidence")
        and path.name.startswith("sample_")
    ):
        return False
    return rel.parts[0] == "docs"


def validate_headings(path: Path, text: str, errors: list[str]) -> None:
    if should_require_heading(path) and not HEADING_PATTERN.search(text):
        errors.append(f"{path}: missing top-level heading")
    if "docs/evidence/" in str(path) and path.name.lower() in {"readme.md", "ci-cd.md"}:
        for section in EVIDENCE_REQUIRED_SECTIONS:
            if section not in text:
                errors.append(f"{path}: missing required section '{section}'")


def validate_links(path: Path, text: str, errors: list[str]) -> None:
    for match in LINK_PATTERN.finditer(text):
        target = match.group(1).strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        target_path = (path.parent / target.split("#", 1)[0]).resolve()
        if not target_path.exists():
            errors.append(f"{path}: broken relative link -> {target}")


def validate_mermaid(path: Path, text: str, errors: list[str]) -> None:
    parts = text.split("```")
    idx = 0
    while idx < len(parts) - 2:
        fence = parts[idx + 1].split("\n", 1)
        if fence[0].strip() != "mermaid":
            idx += 2
            continue
        body = fence[1] if len(fence) > 1 else ""
        body = body.strip()
        if not body:
            errors.append(f"{path}: empty Mermaid block")
        elif not any(body.startswith(kind) for kind in MERMAID_TYPES):
            errors.append(f"{path}: unrecognized Mermaid diagram type")
        idx += 2


def collect_placeholders(files: list[Path]) -> list[str]:
    lines: list[str] = []
    for path in files:
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "[INSERT" in line:
                lines.append(f"- {path.relative_to(ROOT)}:{line_no}: {line.strip()}")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate repository Markdown docs.")
    parser.add_argument(
        "--placeholders-only",
        action="store_true",
        help="Only scan for unresolved [INSERT] placeholders.",
    )
    parser.add_argument(
        "--report-file",
        type=Path,
        help="Write placeholder report to this file.",
    )
    args = parser.parse_args()

    files = iter_markdown_files()
    placeholders = collect_placeholders(files)

    if args.placeholders_only:
        report = ["# Unresolved placeholder report", ""]
        if placeholders:
            report.append(f"Found {len(placeholders)} unresolved placeholder(s):")
            report.extend(placeholders)
        else:
            report.append("No unresolved [INSERT] placeholders found.")
        output = "\n".join(report) + "\n"
        if args.report_file:
            args.report_file.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0

    errors: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        validate_headings(path, text, errors)
        validate_links(path, text, errors)
        validate_mermaid(path, text, errors)

    if errors:
        print("Documentation validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(files)} Markdown file(s).")
    if placeholders:
        print(f"Note: {len(placeholders)} unresolved [INSERT] placeholder(s) reported separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
