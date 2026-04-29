"""
Tagger module — reads and writes audio metadata using mutagen.
Handles FLAC (Vorbis comments) and MP3 (ID3 tags).
"""

import os
from typing import Optional

from mutagen import File as MutagenFile
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TDRC, TRCK


# FLAC stores tags as simple key-value pairs (Vorbis comments)
# this maps their keys to our standard field names
FLAC_TAG_MAP = {
    "title": "title",
    "artist": "artist",
    "album": "album",
    "genre": "genre",
    "date": "year",
    "tracknumber": "track",
}

# MP3 uses ID3 frames with codes like TIT2, TPE1 etc
# found these in the mutagen docs
MP3_TAG_MAP = {
    "TIT2": "title",
    "TPE1": "artist",
    "TALB": "album",
    "TCON": "genre",
    "TDRC": "year",
    "TRCK": "track",
}

# a file needs at least these to be considered "complete"
REQUIRED_FIELDS = {"title", "artist", "album"}


def read_metadata(filepath: str) -> dict:
    """Read tags from an audio file. Returns a dict with standard field names."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()

    metadata = {
        "title": "",
        "artist": "",
        "album": "",
        "genre": "",
        "year": "",
        "track": "",
        "filepath": os.path.abspath(filepath),
        "format": ext.lstrip(".").upper(),
    }

    try:
        if ext == ".flac":
            metadata = _extract_flac(filepath, metadata)
        elif ext == ".mp3":
            metadata = _extract_mp3(filepath, metadata)
        elif ext == ".wav":
            # wav files almost never have metadata, just return defaults
            pass
        else:
            raise ValueError(f"Unsupported format: {ext}")
    except Exception as e:
        metadata["_error"] = str(e)

    return metadata


def _extract_flac(filepath: str, metadata: dict) -> dict:
    """Pull tags from a FLAC file."""
    audio = FLAC(filepath)

    if audio.tags:
        for flac_key, field_name in FLAC_TAG_MAP.items():
            values = audio.tags.get(flac_key, [])
            if values:
                metadata[field_name] = str(values[0]).strip()

    return metadata


def _extract_mp3(filepath: str, metadata: dict) -> dict:
    """Pull tags from an MP3 file."""
    audio = MP3(filepath)

    if audio.tags:
        for id3_key, field_name in MP3_TAG_MAP.items():
            frame = audio.tags.get(id3_key)
            if frame:
                metadata[field_name] = str(frame.text[0]).strip()

    return metadata


def write_metadata(filepath: str, new_tags: dict) -> bool:
    """Write tags back to a file. Returns True if it worked."""
    ext = os.path.splitext(filepath)[1].lower()

    try:
        if ext == ".flac":
            return _write_flac(filepath, new_tags)
        elif ext == ".mp3":
            return _write_mp3(filepath, new_tags)
        else:
            return False
    except Exception:
        return False


def _write_flac(filepath: str, new_tags: dict) -> bool:
    """Write tags to a FLAC file."""
    audio = FLAC(filepath)

    reverse_map = {v: k for k, v in FLAC_TAG_MAP.items()}

    for field_name, value in new_tags.items():
        flac_key = reverse_map.get(field_name)
        if flac_key and value:
            audio[flac_key] = str(value)

    audio.save()
    return True


def _write_mp3(filepath: str, new_tags: dict) -> bool:
    """Write ID3 tags to an MP3 file."""
    audio = MP3(filepath)

    if audio.tags is None:
        audio.add_tags()

    # each ID3 field needs its own frame type
    id3_writers = {
        "title": lambda v: TIT2(encoding=3, text=[v]),
        "artist": lambda v: TPE1(encoding=3, text=[v]),
        "album": lambda v: TALB(encoding=3, text=[v]),
        "genre": lambda v: TCON(encoding=3, text=[v]),
        "year": lambda v: TDRC(encoding=3, text=[v]),
        "track": lambda v: TRCK(encoding=3, text=[v]),
    }

    for field_name, value in new_tags.items():
        writer = id3_writers.get(field_name)
        if writer and value:
            frame = writer(str(value))
            audio.tags.add(frame)

    audio.save()
    return True


def get_metadata_summary(files: list) -> dict:
    """
    Go through a list of files and categorize them as
    complete (all tags), partial (some tags), or missing (no tags).
    """
    summary = {
        "total": len(files),
        "complete": 0,
        "partial": 0,
        "missing": 0,
        "files": [],
    }

    for filepath in files:
        meta = read_metadata(filepath)
        filled = sum(1 for f in REQUIRED_FIELDS if meta.get(f, "").strip())

        if filled == len(REQUIRED_FIELDS):
            status = "complete"
            summary["complete"] += 1
        elif filled > 0:
            status = "partial"
            summary["partial"] += 1
        else:
            status = "missing"
            summary["missing"] += 1

        meta["status"] = status
        summary["files"].append(meta)

    return summary
