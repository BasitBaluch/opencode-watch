"""Resolve a video source (URL, Google Drive, or local path) to a meta dict."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Optional


def is_url(source: str) -> bool:
    return source.startswith("http://") or source.startswith("https://")


def is_google_drive(source: str) -> bool:
    """Check if the source is a Google Drive URL."""
    return "drive.google.com" in source


def hash_source(source: str) -> str:
    return hashlib.sha1(source.encode("utf-8")).hexdigest()


def resolve_source(source: str, focus_range: Optional[tuple[float, float]]) -> dict:
    """Probe the source. Returns:
        {title, duration_s, source, is_url, is_drive, source_hash, focus_range_str}
    """
    focus_str = "" if focus_range is None else f"{focus_range[0]}-{focus_range[1]}"

    if is_google_drive(source):
        # Google Drive: can't probe before download, use placeholder title
        file_id_match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", source) or \
                        re.search(r"id=([a-zA-Z0-9_-]+)", source)
        file_id = file_id_match.group(1) if file_id_match else "unknown"
        return {
            "title": f"Google Drive Video ({file_id[:8]})",
            "duration_s": 0.0,  # Unknown until after download
            "source": source,
            "is_url": True,
            "is_drive": True,
            "source_hash": hash_source(source),
            "focus_range_str": focus_str,
        }

    if is_url(source):
        proc = subprocess.run(
            ["yt-dlp", "-j", "--no-playlist", source],
            capture_output=True, text=True, check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"yt-dlp probe failed: {proc.stderr.strip()}")
        info = json.loads(proc.stdout)
        return {
            "title": info.get("title") or info.get("id") or "untitled",
            "duration_s": float(info.get("duration") or 0.0),
            "source": source,
            "is_url": True,
            "is_drive": False,
            "source_hash": hash_source(source),
            "focus_range_str": focus_str,
        }

    p = Path(source).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"local file not found: {p}")
    proc = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1",
            str(p),
        ],
        capture_output=True, text=True, check=True,
    )
    duration = float(proc.stdout.strip() or 0.0)
    return {
        "title": p.stem,
        "duration_s": duration,
        "source": str(p),
        "is_url": False,
        "is_drive": False,
        "source_hash": hash_source(str(p)),
        "focus_range_str": focus_str,
    }
