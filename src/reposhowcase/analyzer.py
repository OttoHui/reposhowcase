from __future__ import annotations

import ast
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

import tomllib

from .models import Evidence, RepositoryReport

LANGUAGES = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".rb": "Ruby",
    ".php": "PHP", ".cs": "C#", ".cpp": "C++", ".c": "C",
    ".swift": "Swift", ".vue": "Vue", ".html": "HTML", ".css": "CSS",
}
IGNORED = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"}
MANIFESTS = {
    "pyproject.toml", "requirements.txt", "package.json", "go.mod",
    "Cargo.toml", "pom.xml", "Gemfile", "composer.json",
}


def _files(root: Path) -> list[Path]:
    return [
        path for path in root.rglob("*")
        if path.is_file() and not any(part in IGNORED for part in path.parts)
    ]


def _python_symbols(path: Path) -> int:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, SyntaxError):
        return 0
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and not node.name.startswith("_")
        for node in ast.walk(tree)
    )


def _git_contributors(root: Path) -> int:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "shortlog", "-sne", "HEAD"],
            check=False, capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 0
    return len([line for line in result.stdout.splitlines() if line.strip()])


def _dependencies(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.name == "package.json":
        try:
            package = json.loads(text)
        except json.JSONDecodeError:
            return []
        if not isinstance(package, dict):
            return []
        sections = ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies")
        return sorted({
            name for section in sections
            for name in package.get(section, {})
            if isinstance(name, str)
        })
    if path.name in {"requirements.txt", "Gemfile"}:
        names = set()
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith(("#", "-", "git+", "http")):
                continue
            names.add(re.split(r"[<>=!~;\[\s]", line, maxsplit=1)[0])
        return sorted(names)
    if path.name == "pyproject.toml":
        try:
            project = tomllib.loads(text).get("project", {})
        except tomllib.TOMLDecodeError:
            return []
        return sorted({
            re.split(r"[<>=!~;\[\s]", requirement, maxsplit=1)[0]
            for requirement in project.get("dependencies", [])
            if isinstance(requirement, str)
        })
    return sorted(set(re.findall(r'(?m)^\s*([A-Za-z][A-Za-z0-9_.-]+)\s*=', text)))[:30]


def analyze_repository(repository: str | Path) -> RepositoryReport:
    """Scan *repository* and return facts with paths that support them."""
    root = Path(repository).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Repository directory does not exist: {root}")
    paths = _files(root)
    counts = Counter(LANGUAGES[path.suffix.lower()] for path in paths if path.suffix.lower() in LANGUAGES)
    languages = [name for name, _ in counts.most_common()]
    source_paths = [path for path in paths if path.suffix.lower() in LANGUAGES]
    test_paths = [path for path in paths if "test" in path.name.lower() or "tests" in path.parts]
    evidence: list[Evidence] = []

    readme = next((p for p in paths if p.name.lower() in {"readme.md", "readme.rst", "readme.txt"}), None)
    excerpt = ""
    if readme:
        readme_text = readme.read_text(encoding="utf-8", errors="ignore").strip()
        excerpt = readme_text[:500]
        evidence.append(Evidence(str(readme.relative_to(root)), "documentation", "Project README"))
    for path in paths:
        if path.name in MANIFESTS:
            deps = _dependencies(path)
            evidence.append(Evidence(str(path.relative_to(root)), "manifest", f"{len(deps)} declared dependencies"))
    for path in test_paths[:10]:
        evidence.append(Evidence(str(path.relative_to(root)), "tests", "Test source"))
    for path in source_paths[:10]:
        evidence.append(Evidence(str(path.relative_to(root)), "source", f"{LANGUAGES[path.suffix.lower()]} source"))

    commands = re.findall(r"(?m)^\s*(?:\$|>)\s*(.+)$", readme_text) if readme else []
    return RepositoryReport(
        root=root, name=root.name, languages=languages,
        source_files=len(source_paths), test_files=len(test_paths),
        public_symbols=sum(_python_symbols(p) for p in source_paths if p.suffix == ".py"),
        dependencies=sorted({dep for path in paths if path.name in MANIFESTS for dep in _dependencies(path)}),
        contributors=_git_contributors(root), evidence=evidence,
        commands=commands[:8], readme_excerpt=excerpt,
    )
