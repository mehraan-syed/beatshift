"""
Scanner module — finds audio files in a directory.
"""

import os
from pathlib import Path
from typing import List

# formats we support
SUPPORTED_EXTENSIONS = {".flac", ".mp3", ".wav"}


def scan_directory(path: str, extensions: set = None) -> List[str]:
    """Recursively scan a directory and return paths to audio files."""
    if extensions is None:
        extensions = SUPPORTED_EXTENSIONS

    root = Path(path)

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    audio_files = []

    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in extensions:
                full_path = os.path.join(dirpath, filename)
                audio_files.append(os.path.abspath(full_path))

    audio_files.sort()
    return audio_files


def find_duplicates(files: list, metadata_fn=None) -> List[tuple]:
    """
    Find files that might be duplicates by comparing their
    title/artist/album metadata. Groups files with identical
    metadata together.
    """
    if metadata_fn is None:
        return []

    seen = {}

    for filepath in files:
        try:
            meta = metadata_fn(filepath)
            key = (
                meta.get("title", "").lower().strip(),
                meta.get("artist", "").lower().strip(),
                meta.get("album", "").lower().strip(),
            )
            # skip files with no useful metadata at all
            if all(k == "" for k in key):
                continue

            if key not in seen:
                seen[key] = []
            seen[key].append(filepath)
        except Exception:
            continue

    return [tuple(paths) for paths in seen.values() if len(paths) > 1]
