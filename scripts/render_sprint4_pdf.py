#!/usr/bin/env python3
"""Render the Sprint 4 Markdown report to PDF with Mermaid diagrams."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "FluentEdge_Sprint4_Prototype_Implementation_Document.md"
DEFAULT_OUTPUT = ROOT / "FluentEdge_Sprint4_Prototype_Implementation_Document.pdf"
TEMP_PYTHON = Path("/tmp/fluentedge-pdf/python")
MERMAID_JS = Path("/tmp/fluentedge-pdf/node/node_modules/mermaid/dist/mermaid.min.js")

CSS = """
@page { size: Letter; margin: 0.65in 0.62in 0.72in; }
:root { color-scheme: light; }
body {
  color: #17202a;
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 9.3pt;
  line-height: 1.38;
  margin: 0;
}
h1, h2, h3, h4 { color: #123d5a; page-break-after: avoid; }
h1 { border-bottom: 2px solid #2f7d69; font-size: 22pt; margin: 0 0 16px; padding-bottom: 7px; }
h2 { font-size: 15pt; margin: 18px 0 8px; }
h3 { font-size: 11.5pt; margin: 14px 0 6px; }
h4 { font-size: 10pt; margin: 12px 0 5px; }
p { margin: 5px 0 8px; }
a { color: #155b86; text-decoration: none; }
blockquote {
  background: #edf5f2; border-left: 4px solid #2f7d69; margin: 10px 0; padding: 7px 11px;
}
code {
  background: #eef1f3; border-radius: 2px; font-family: "Liberation Mono", monospace;
  font-size: 8.4pt; padding: 1px 3px;
}
pre { background: #f4f6f7; border: 1px solid #d5dadd; padding: 9px; white-space: pre-wrap; }
pre code { background: transparent; padding: 0; }
table { border-collapse: collapse; font-size: 7.8pt; margin: 8px 0 13px; width: 100%; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { background: #dceae6; color: #123d5a; font-weight: 700; }
th, td { border: 1px solid #9caeb5; padding: 4px 5px; text-align: left; vertical-align: top; }
ul, ol { margin: 5px 0 9px; padding-left: 23px; }
li { margin: 2px 0; }
.page-break { break-before: page; height: 0; }
.mermaid { break-inside: avoid; margin: 12px auto 18px; text-align: center; }
.mermaid svg { height: auto !important; max-height: 8.1in; max-width: 100% !important; }
body > h1:first-of-type {
  border: 0; color: #0d344d; font-size: 30pt; margin-top: 0.8in; text-align: center;
}
body > h1:first-of-type + h2 { color: #2f7d69; font-size: 20pt; text-align: center; }
"""


def render_markdown(source: Path) -> str:
    if TEMP_PYTHON.exists():
        sys.path.insert(0, str(TEMP_PYTHON))
    try:
        import markdown
    except ImportError as exc:
        raise RuntimeError(
            "Install Markdown under /tmp/fluentedge-pdf/python before rendering"
        ) from exc
    return markdown.markdown(
        source.read_text(encoding="utf-8"),
        extensions=["attr_list", "fenced_code", "tables", "toc"],
    )


def render_pdf(source: Path, output: Path) -> None:
    if not MERMAID_JS.is_file():
        raise FileNotFoundError(f"Mermaid renderer not found: {MERMAID_JS}")
    document = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{render_markdown(source)}</body>
</html>"""

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 960})
        page.set_content(document, wait_until="load")
        page.evaluate(
            """() => {
              document.querySelectorAll('pre code.language-mermaid').forEach((code) => {
                const diagram = document.createElement('div');
                diagram.className = 'mermaid';
                diagram.textContent = code.textContent;
                code.parentElement.replaceWith(diagram);
              });
            }"""
        )
        page.add_script_tag(path=str(MERMAID_JS))
        page.evaluate(
            """async () => {
              mermaid.initialize({ startOnLoad: false, theme: 'neutral', securityLevel: 'strict' });
              await mermaid.run({ querySelector: '.mermaid' });
              await document.fonts.ready;
            }"""
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        page.pdf(
            path=str(output),
            format="Letter",
            print_background=True,
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=(
                "<div style='font-size:8px;color:#53636b;text-align:center;width:100%;'>"
                "FluentEdge Sprint 4 | Page <span class='pageNumber'></span> of "
                "<span class='totalPages'></span></div>"
            ),
            margin={"top": "0.65in", "right": "0.62in", "bottom": "0.72in", "left": "0.62in"},
        )
        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    render_pdf(args.source.resolve(), args.output.resolve())
    print(f"Wrote {args.output.resolve()}")


if __name__ == "__main__":
    main()
