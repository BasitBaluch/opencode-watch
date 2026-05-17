"""yt-dlp download wrapper + Google Drive + local file linker."""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


def _extract_drive_file_id(url: str) -> str | None:
    """Extract Google Drive file ID from various URL formats."""
    patterns = [
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"id=([a-zA-Z0-9_-]+)",
        r"/open\?id=([a-zA-Z0-9_-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def download_from_drive(url: str, out_dir: Path, *, basename: str = "video") -> Path:
    """Download from Google Drive using gdown (free, no API key needed)."""
    file_id = _extract_drive_file_id(url)
    if not file_id:
        raise RuntimeError(f"Could not extract Google Drive file ID from: {url}")

    out_dir.mkdir(parents=True, exist_ok=True)
    # gdown needs the URL in a specific format
    drive_url = f"https://drive.google.com/uc?id={file_id}"

    cmd = [
        "gdown",
        "--id", file_id,
        "-O", str(out_dir / f"{basename}.mp4"),
        "--fuzzy",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        # Retry with URL-based approach
        cmd2 = ["gdown", drive_url, "-O", str(out_dir / f"{basename}.mp4"), "--fuzzy"]
        proc2 = subprocess.run(cmd2, capture_output=True, text=True, check=False)
        if proc2.returncode != 0:
            raise RuntimeError(
                f"gdown failed: {proc2.stderr.strip() or proc.stderr.strip()}"
            )

    matches = sorted(out_dir.glob(f"{basename}.*"))
    if not matches:
        raise RuntimeError(f"gdown returned 0 but no {basename}.* file in {out_dir}")
    return matches[0]


def download_video(url: str, out_dir: Path, *, basename: str = "video") -> Path:
    """Download to `out_dir/<basename>.<ext>` via yt-dlp. Returns the downloaded file."""
    out_dir.mkdir(parents=True, exist_ok=True)
    template = str(out_dir / f"{basename}.%(ext)s")
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "-f", "best[ext=mp4]/best",
        "-o", template,
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {proc.stderr.strip()}")
    matches = sorted(out_dir.glob(f"{basename}.*"))
    if not matches:
        raise RuntimeError(f"yt-dlp returned 0 but no {basename}.* file in {out_dir}")
    return matches[0]


def copy_local(src: Path, out_dir: Path, *, basename: str = "video") -> Path:
    """For local sources, symlink (cheap, no copy) into out_dir/<basename>.<ext>.
    Falls back to a regular file copy if symlink fails."""
    out_dir.mkdir(parents=True, exist_ok=True)
    src = src.expanduser().resolve()
    dst = out_dir / f"{basename}{src.suffix}"
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    try:
        os.symlink(src, dst)
    except OSError:
        dst.write_bytes(src.read_bytes())
    return dst
