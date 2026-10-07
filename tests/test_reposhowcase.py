from pathlib import Path

from reposhowcase import analyze_repository, build_storyboard
from reposhowcase.exporters.html import export_html


def test_analyze_and_export(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Demo\nRun it with `$ demo run`.\n")
    (tmp_path / "main.py").write_text("def public_api():\n    return 1\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text("def test_it(): pass\n")

    report = analyze_repository(tmp_path)
    assert report.languages == ["Python"]
    assert report.source_files == 2
    assert report.test_files == 1
    assert report.public_symbols == 2
    storyboard = build_storyboard(report)
    destination = export_html(storyboard, tmp_path / "showcase.html")
    assert destination.read_text().count("class=\"slide\"") == 4


def test_manifest_dependencies_and_readme_commands(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Demo\n$ python -m demo\n")
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'dependencies = ["requests>=2", "rich"]\n'
    )
    (tmp_path / "package.json").write_text(
        '{"dependencies": {"react": "^1"}, "scripts": {"build": "x"}}\n'
    )

    report = analyze_repository(tmp_path)

    assert report.dependencies == ["react", "requests", "rich"]
    assert report.commands == ["python -m demo"]


def test_invalid_repository_is_rejected(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    try:
        analyze_repository(missing)
    except NotADirectoryError as exc:
        assert str(missing) in str(exc)
    else:
        raise AssertionError("analyze_repository should reject a missing directory")
