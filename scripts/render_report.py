"""Render ``report/report.md`` to ``report/report.pdf`` (Markdown → HTML → PDF with WeasyPrint).

Images are resolved relative to ``report/``; Chinese text uses ``report/fonts/NotoSansSC.ttf``.

Usage::

    pip install markdown weasyprint
    python3 scripts/render_report.py
"""
from __future__ import annotations

from pathlib import Path

import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "report"
FONT = REPORT_DIR / "fonts" / "NotoSansSC.ttf"

CSS = f"""
@font-face {{ font-family: 'Noto Sans SC'; src: url('{FONT.as_uri()}'); }}
@page {{ size: A4; margin: 18mm 16mm 20mm;
         @bottom-center {{ content: counter(page) ' / ' counter(pages); font-size: 9pt; color: #777; }} }}
body {{ font-family: 'Noto Sans SC', sans-serif; font-size: 10.5pt; line-height: 1.6; color: #1a1a1a; }}
h1 {{ font-size: 20pt; margin: 0 0 4pt; }}
h2 {{ font-size: 14pt; margin: 18pt 0 6pt; padding-bottom: 3pt; border-bottom: 1px solid #ddd;
      page-break-after: avoid; }}
h3 {{ font-size: 11.5pt; margin: 12pt 0 4pt; page-break-after: avoid; }}
p, li {{ margin: 4pt 0; }}
hr {{ border: none; border-top: 1px solid #e4e3df; margin: 12pt 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 9.5pt; page-break-inside: avoid; }}
th, td {{ border: 1px solid #d9d8d3; padding: 4pt 6pt; text-align: left; vertical-align: top; }}
th {{ background: #f3f2ee; }}
code {{ font-family: 'DejaVu Sans Mono', monospace; font-size: 9pt; background: #f3f2ee; padding: 0 2pt; border-radius: 2pt; }}
img {{ width: 100%; margin: 6pt 0 0; page-break-inside: avoid; }}
p:has(> img) {{ page-break-inside: avoid; page-break-after: avoid; }}
em {{ color: #52514e; font-size: 9pt; font-style: normal; }}
"""


def main() -> None:
    md_text = (REPORT_DIR / "report.md").read_text(encoding="utf-8")
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])
    html = f"<!doctype html><html lang='zh'><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
    out = REPORT_DIR / "report.pdf"
    HTML(string=html, base_url=str(REPORT_DIR) + "/").write_pdf(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
