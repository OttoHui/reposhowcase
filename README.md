# RepoShowcase

RepoShowcase analyzes an existing multi-language software repository and turns
verified repository facts into an evidence-based project showcase. The same
storyboard can be exported as an interactive HTML presentation, an editable
PowerPoint file, or an MP4 video.

## Motivation

Explaining an unfamiliar software project usually requires manually collecting
facts from its README, source tree, dependency files, tests, and Git history.
That process is slow and can lead to claims that are difficult to verify.
RepoShowcase automates the evidence-gathering stage while keeping each claim
linked to the repository-relative path that supports it.

## What makes it different

- **Evidence before presentation:** generated claims come from files and Git
  data found in the repository rather than invented project descriptions.
- **One model, three outputs:** HTML, PPTX, and MP4 are generated from the same
  storyboard, so the formats remain consistent.
- **Multi-language fallback:** common languages receive file-level detection,
  while unfamiliar file types still contribute generic repository evidence.
- **Useful for existing projects:** the target repository does not need to
  follow a special framework or add RepoShowcase-specific annotations.

## Example use cases

- Give a one-minute overview of a team software project.
- Create a review presentation for an unfamiliar open-source repository.
- Produce an evidence-backed project summary for a class demonstration.
- Generate a machine-readable JSON report for later analysis or tooling.

## Quick start

```bash
pip install -e ".[dev]"
reposhowcase build ./my-project --outputs html,pptx,mp4 --output showcase/
```

HTML is dependency-free. PPTX requires the `pptx` extra, and MP4 requires an
`ffmpeg` executable on `PATH`. If the installed FFmpeg build does not include
the optional `drawtext` filter, MP4 export still succeeds with clean color
slides without text overlays.

After the first PyPI release, the installation command will become:

```bash
pip install reposhowcase
```

For development with optional exporters and test tools:

```bash
pip install -e ".[dev,pptx]"
```

## Analysis pipeline

```text
scan repository
    -> detect languages and project files
    -> extract README, dependency, test, symbol, and Git evidence
    -> build a four-slide storyboard
    -> export HTML, PPTX, MP4, or JSON
```

The default storyboard contains:

1. **Project idea** — README-based project description
2. **How it works** — languages, source files, and dependencies
3. **Evidence** — tests, public Python symbols, and contributors
4. **Demo** — commands found in the README and next steps

## Python API

```python
from reposhowcase import analyze_repository, build_storyboard
from reposhowcase.exporters import export_html

report = analyze_repository("./my-project")
storyboard = build_storyboard(report, duration=60)
export_html(storyboard, "showcase.html")
```

The analyzer deliberately reports unknown languages and generic file evidence
instead of guessing unsupported details. The CLI also supports `json`, which
writes the analyzed report as machine-readable data.

## Team

RepoShowcase is developed by a six-member student project team for the
CS1302A Agentic Coding project. Team member names will be added before the
public project release.

## Development

The package uses a `src/` layout. Run the focused checks from the repository
root:

```bash
python -m pytest
python -m ruff check src tests
```

The public repository will contain the project history, documentation,
automated checks, and release information. Personal contact details and
student IDs should not be included in the package.
