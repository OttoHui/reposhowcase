from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import analyze_repository
from .exporters.html import export_html
from .exporters.mp4 import export_mp4
from .exporters.pptx import export_pptx
from .storyboard import build_storyboard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="reposhowcase")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="Analyze a repository and export a showcase")
    build.add_argument("repository", type=Path)
    build.add_argument("--outputs", default="html", help="Comma-separated: html,pptx,mp4,json")
    build.add_argument("--duration", type=float, default=60)
    build.add_argument("--output", type=Path, default=Path("showcase"))
    args = parser.parse_args(argv)
    report = analyze_repository(args.repository)
    storyboard = build_storyboard(report, args.duration)
    args.output.mkdir(parents=True, exist_ok=True)
    outputs = {item.strip().lower() for item in args.outputs.split(",")}
    if "html" in outputs:
        export_html(storyboard, args.output / "showcase.html")
    if "pptx" in outputs:
        export_pptx(storyboard, args.output / "showcase.pptx")
    if "mp4" in outputs:
        export_mp4(storyboard, args.output / "showcase.mp4")
    if "json" in outputs:
        (args.output / "report.json").write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    print(f"Analyzed {report.name}: {len(storyboard.slides)} slides written to {args.output}")
    return 0
