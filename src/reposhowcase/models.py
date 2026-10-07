from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Evidence:
    """A claim-supporting repository location and a short extracted detail."""

    path: str
    kind: str
    detail: str


@dataclass
class RepositoryReport:
    root: Path
    name: str
    languages: list[str]
    source_files: int
    test_files: int
    public_symbols: int
    dependencies: list[str]
    contributors: int
    evidence: list[Evidence] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    readme_excerpt: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "languages": self.languages,
            "source_files": self.source_files,
            "test_files": self.test_files,
            "public_symbols": self.public_symbols,
            "dependencies": self.dependencies,
            "contributors": self.contributors,
            "evidence": [e.__dict__ for e in self.evidence],
            "commands": self.commands,
        }


@dataclass(frozen=True)
class Slide:
    number: int
    title: str
    body: str
    bullets: tuple[str, ...] = ()
    evidence: tuple[Evidence, ...] = ()
    seconds: float = 0


@dataclass(frozen=True)
class Storyboard:
    title: str
    slides: tuple[Slide, ...]
    duration: float

