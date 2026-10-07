from __future__ import annotations

from .models import RepositoryReport, Slide, Storyboard


def build_storyboard(report: RepositoryReport, duration: float = 60) -> Storyboard:
    if duration <= 0:
        raise ValueError("duration must be greater than zero")
    durations = [duration * ratio for ratio in (0.2, 0.3, 0.3, 0.2)]
    evidence = tuple(report.evidence)
    return Storyboard(
        title=f"{report.name}: repository showcase",
        duration=duration,
        slides=(
            Slide(1, "Project idea", "What the repository is built to do.",
                  (report.readme_excerpt or "No README evidence found.",), evidence[:2], durations[0]),
            Slide(2, "How it works", "Languages, source files, and dependencies.",
                  (f"Languages: {', '.join(report.languages) or 'Unknown'}",
                   f"{report.source_files} source files and {len(report.dependencies)} dependencies"),
                  tuple(e for e in evidence if e.kind in {"source", "manifest"}), durations[1]),
            Slide(3, "Evidence", "Quality signals found in the repository.",
                  (f"{report.test_files} test files", f"{report.public_symbols} public Python symbols",
                   f"{report.contributors or 'No'} Git contributors detected"),
                  tuple(e for e in evidence if e.kind in {"tests", "documentation"}), durations[2]),
            Slide(4, "Demo", "Commands and next steps.",
                  tuple(report.commands or ("Inspect the generated evidence report.",)),
                  evidence[-3:], durations[3]),
        ),
    )

