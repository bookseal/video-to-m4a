#!/usr/bin/env python3
"""video_to_m4a — 최근 동영상 파일을 골라 같은 이름의 .m4a 오디오로 변환한다.

사용법:
    python3 video_to_m4a.py
"""

from __future__ import annotations

from datetime import datetime
import shutil
import subprocess
import sys
from pathlib import Path

# 동영상으로 취급할 확장자
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".flv", ".wmv"}

# 스캔할 디렉터리와 목록에 보여줄 최대 개수
SCAN_DIR = Path.cwd()
MAX_LIST = 10


def human_size(num_bytes: int) -> str:
    """바이트 수를 사람이 읽기 좋은 문자열로."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def created_stamp(path: Path) -> str:
    """파일 생성 시각을 '20260608_230503' 형식 문자열로 반환.

    macOS는 생성 시각(st_birthtime)을 지원하므로 우선 사용하고,
    없으면 수정 시각(st_mtime)으로 폴백한다.
    """
    st = path.stat()
    ts = getattr(st, "st_birthtime", st.st_mtime)
    return datetime.fromtimestamp(ts).strftime("%Y%m%d_%H%M%S")


def find_recent_videos(directory: Path, limit: int) -> list[Path]:
    """디렉터리에서 동영상 파일을 찾아 최신 수정 시각 순으로 정렬해 반환."""
    videos = [
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in VIDEO_EXTS
    ]
    videos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return videos[:limit]


def choose_video(videos: list[Path]) -> Path | None:
    """동영상 목록을 보여주고 사용자가 하나 고르게 한다."""
    print("\n최근 동영상 파일:\n")
    for i, p in enumerate(videos, 1):
        size = human_size(p.stat().st_size)
        print(f"  [{i}] {p.name}  ({size})")
    print()

    raw = input(f"변환할 번호를 선택하세요 (1-{len(videos)}, 취소: Enter): ").strip()
    if not raw:
        return None
    if not raw.isdigit() or not (1 <= int(raw) <= len(videos)):
        print("잘못된 입력입니다.")
        return None
    return videos[int(raw) - 1]


def build_ffmpeg_command(src: Path, dst: Path) -> list[str]:
    """src 동영상을 dst(.m4a)로 변환하는 ffmpeg 명령어 리스트를 만든다.

    subprocess.run()에 넘길 인자 리스트 형태로 반환한다.
    예: ["ffmpeg", "-i", str(src), ..., str(dst)]
    """
    return [
        "ffmpeg",
        "-y",            # 이미 사용자에게 덮어쓰기를 물었으므로 ffmpeg는 묻지 않음
        "-i", str(src),  # 입력 동영상
        "-vn",           # 비디오 스트림 제거 (오디오만)
        "-c:a", "aac",   # AAC로 재인코딩 (원본 코덱과 무관하게 항상 동작)
        "-b:a", "192k",  # 오디오 비트레이트
        str(dst),        # 출력 .m4a
    ]


def main() -> int:
    if shutil.which("ffmpeg") is None:
        print("ffmpeg가 설치되어 있지 않습니다. 먼저 설치하세요:")
        print("    brew install ffmpeg")
        return 1

    videos = find_recent_videos(SCAN_DIR, MAX_LIST)
    if not videos:
        print(f"'{SCAN_DIR}' 에서 동영상 파일을 찾지 못했습니다.")
        return 1

    src = choose_video(videos)
    if src is None:
        print("취소되었습니다.")
        return 0

    dst = src.with_name(f"{src.stem}_{created_stamp(src)}.m4a")
    if dst.exists():
        ans = input(f"'{dst.name}' 이(가) 이미 있습니다. 덮어쓸까요? (y/N): ").strip().lower()
        if ans != "y":
            print("취소되었습니다.")
            return 0

    cmd = build_ffmpeg_command(src, dst)
    print(f"\n변환 중: {src.name} → {dst.name}\n")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("\n변환 실패.")
        return 1

    print(f"\n완료: {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
