"""
Organizer module — moves and renames audio files into a
clean folder structure based on their metadata.
"""

import os
import shutil
import re
from pathlib import Path
from typing import List


DEFAULT_PATTERN = "{artist}/{album}/{track} - {title}"


def organize_files(
    files_metadata: list,
    dest: str,
    pattern: str = None,
    dry_run: bool = False,
) -> List[dict]:
    """
    Take a list of file metadata dicts and move/rename the files
    into a folder structure. If dry_run is True, just show what
    would happen without actually moving anything.
    """
    if pattern is None:
        pattern = DEFAULT_PATTERN

    results = []

    for meta in files_metadata:
        src_path = meta.get("filepath", "")

        if not src_path or not os.path.isfile(src_path):
            results.append({
                "src": src_path,
                "dest": "",
                "status": "skipped",
                "reason": "file not found",
            })
            continue

        new_path = build_new_path(meta, dest, pattern)

        if not new_path:
            results.append({
                "src": src_path,
                "dest": "",
                "status": "skipped",
                "reason": "insufficient metadata",
            })
            continue

        if dry_run:
            results.append({
                "src": src_path,
                "dest": new_path,
                "status": "preview",
            })
        else:
            success = _safe_move(src_path, new_path)
            results.append({
                "src": src_path,
                "dest": new_path,
                "status": "moved" if success else "failed",
            })

    return results


def build_new_path(metadata: dict, dest: str, pattern: str) -> str:
    """Build a destination path from metadata and a pattern like {artist}/{album}/{track} - {title}."""
    artist = _sanitize(metadata.get("artist", ""))
    album = _sanitize(metadata.get("album", ""))
    title = _sanitize(metadata.get("title", ""))
    track = metadata.get("track", "").strip()

    # need at least artist and title to build a proper path
    if not artist or not title:
        return ""

    # pad track number so files sort properly (3 -> 03)
    if track:
        try:
            # handle formats like "3/12" (track 3 of 12)
            track_num = track.split("/")[0].strip()
            track = str(int(track_num)).zfill(2)
        except ValueError:
            track = "00"
    else:
        track = "00"

    if not album:
        album = "Unknown Album"

    ext = os.path.splitext(metadata.get("filepath", ""))[1].lower()

    relative = pattern.format(
        artist=artist,
        album=album,
        track=track,
        title=title,
    )

    return os.path.join(dest, relative + ext)


def _sanitize(value: str) -> str:
    """Clean a string so it's safe to use as a file/folder name."""
    if not value:
        return ""

    value = value.strip()

    # remove characters that windows doesn't allow in filenames
    value = re.sub(r'[<>:"/\\|?*]', '', value)

    # collapse multiple spaces into one
    value = re.sub(r'\s+', ' ', value)

    # dots at the start/end cause issues on windows
    value = value.strip('.')

    return value


def _safe_move(src: str, dest: str) -> bool:
    """
    Move a file, creating folders as needed. If something already
    exists at the destination, add a number to avoid overwriting.
    """
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        # don't overwrite — add (1), (2) etc if file exists
        if os.path.exists(dest):
            base, ext = os.path.splitext(dest)
            counter = 1
            while os.path.exists(f"{base} ({counter}){ext}"):
                counter += 1
            dest = f"{base} ({counter}){ext}"

        shutil.move(src, dest)
        return True

    except (OSError, shutil.Error):
        return False
