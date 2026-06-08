#!/usr/bin/env python3
"""video_to_m4a - pick a recent video and convert it to an .m4a audio file.

Usage:
    python3 video_to_m4a.py
"""

from __future__ import annotations

from datetime import datetime
import shutil
import subprocess
import sys
from pathlib import Path

# File extensions treated as videos.
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".flv", ".wmv"}

# Directory to scan and the max number of files to list.
SCAN_DIR = Path.cwd()
MAX_LIST = 10


def human_size(num_bytes: int) -> str:
    """Format a byte count as a short human-readable string."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def created_stamp(path: Path) -> str:
    """Return the file's creation time as 'YYYYMMDD_HHMM' (e.g. '20260608_1405').

    macOS exposes the creation time via st_birthtime; fall back to the
    modification time (st_mtime) when it is not available.
    """
    st = path.stat()
    ts = getattr(st, "st_birthtime", st.st_mtime)
    return datetime.fromtimestamp(ts).strftime("%Y%m%d_%H%M")


def find_recent_videos(directory: Path, limit: int) -> list[Path]:
    """Find video files in a directory, newest modified first."""
    videos = [
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in VIDEO_EXTS
    ]
    videos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return videos[:limit]


def choose_video(videos: list[Path]) -> Path | None:
    """Show the list of videos and let the user pick one."""
    print("\nRecent video files:\n")
    for i, p in enumerate(videos, 1):
        size = human_size(p.stat().st_size)
        print(f"  [{i}] {p.name}  ({size})")
    print()

    raw = input(f"Select a number to convert (1-{len(videos)}, Enter to cancel): ").strip()
    if not raw:
        return None
    if not raw.isdigit() or not (1 <= int(raw) <= len(videos)):
        print("Invalid input.")
        return None
    return videos[int(raw) - 1]


def prompt_output_path(src: Path) -> Path:
    """Build the output path. The timestamp prefix is fixed; the user can
    type the rest of the name, or press Enter to keep the original name."""
    prefix = f"{created_stamp(src)}_"          # e.g. "20260608_1405_"
    default_suffix = src.stem                   # original name without extension
    print(f"\nOutput name example: {prefix}{default_suffix}.m4a")

    suffix = input(f"Type a name after '{prefix}' (Enter to keep '{default_suffix}'): ").strip()
    if not suffix:
        suffix = default_suffix
    return src.with_name(f"{prefix}{suffix}.m4a")


def build_ffmpeg_command(src: Path, dst: Path) -> list[str]:
    """Build the ffmpeg argument list that converts src into dst (.m4a)."""
    return [
        "ffmpeg",
        "-y",            # we already asked before overwriting, so don't prompt
        "-i", str(src),  # input video
        "-vn",           # drop the video stream (audio only)
        "-c:a", "aac",   # re-encode to AAC (works for any source codec)
        "-b:a", "192k",  # audio bitrate
        str(dst),        # output .m4a
    ]


def main() -> int:
    if shutil.which("ffmpeg") is None:
        print("ffmpeg is not installed. Install it first:")
        print("    brew install ffmpeg")
        return 1

    videos = find_recent_videos(SCAN_DIR, MAX_LIST)
    if not videos:
        print(f"No video files found in '{SCAN_DIR}'.")
        return 1

    src = choose_video(videos)
    if src is None:
        print("Cancelled.")
        return 0

    dst = prompt_output_path(src)
    if dst.exists():
        ans = input(f"'{dst.name}' already exists. Overwrite? (y/N): ").strip().lower()
        if ans != "y":
            print("Cancelled.")
            return 0

    cmd = build_ffmpeg_command(src, dst)
    print(f"\nConverting: {src.name} -> {dst.name}\n")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("\nConversion failed.")
        return 1

    print(f"\nDone: {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
