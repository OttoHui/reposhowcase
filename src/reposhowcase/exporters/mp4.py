from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from ..models import Storyboard


def export_mp4(storyboard: Storyboard, output: str | Path) -> Path:
    """Render a storyboard to a simple, portable H.264 slide video."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("MP4 export requires ffmpeg installed and available on PATH.")
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="reposhowcase-") as temp:
        temp_path = Path(temp)
        clips: list[Path] = []
        for index, slide in enumerate(storyboard.slides):
            text_file = temp_path / f"{index}.txt"
            text_file.write_text(
                f"{slide.title}\n\n{slide.body}\n\n"
                + "\n".join(f"- {bullet}" for bullet in slide.bullets),
                encoding="utf-8",
            )
            clip = temp_path / f"{index}.mp4"
            _run_ffmpeg(
                ffmpeg,
                "-y", "-loglevel", "error",
                "-f", "lavfi", "-i", "color=c=173b8f:s=1280x720:r=30",
                "-t", str(slide.seconds), "-vf",
                f"drawtext=textfile={text_file}:fontcolor=white:fontsize=40:"
                "line_spacing=14:x=70:y=150",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip),
            )
            clips.append(clip)
        concat = temp_path / "concat.txt"
        concat.write_text(
            "".join(f"file '{clip.as_posix()}'\n" for clip in clips),
            encoding="utf-8",
        )
        _run_ffmpeg(
            ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
            "-i", str(concat), "-c", "copy", str(destination),
        )
    return destination


def _run_ffmpeg(ffmpeg: str, *arguments: str) -> None:
    try:
        subprocess.run([ffmpeg, *arguments], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "ffmpeg failed").strip()
        raise RuntimeError(f"MP4 export failed: {detail}") from exc
