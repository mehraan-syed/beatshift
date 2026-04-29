"""
Stats module — calculates numbers about a music collection.
"""

import os
from typing import List


def collection_stats(files_metadata: list) -> dict:
    """Count up stats from a list of file metadata dicts."""
    stats = {
        "total_files": len(files_metadata),
        "by_format": {},
        "by_genre": {},
        "by_artist": {},
        "total_size_bytes": 0,
        "total_size_mb": 0.0,
        "complete_tags": 0,
        "incomplete_tags": 0,
    }

    for meta in files_metadata:
        # count formats
        fmt = meta.get("format", "UNKNOWN")
        stats["by_format"][fmt] = stats["by_format"].get(fmt, 0) + 1

        # count genres
        genre = meta.get("genre", "").strip()
        if genre:
            stats["by_genre"][genre] = stats["by_genre"].get(genre, 0) + 1
        else:
            stats["by_genre"]["Unknown"] = stats["by_genre"].get("Unknown", 0) + 1

        # count artists
        artist = meta.get("artist", "").strip()
        if artist:
            stats["by_artist"][artist] = stats["by_artist"].get(artist, 0) + 1
        else:
            stats["by_artist"]["Unknown"] = stats["by_artist"].get("Unknown", 0) + 1

        # tag completeness
        status = meta.get("status", "")
        if status == "complete":
            stats["complete_tags"] += 1
        else:
            stats["incomplete_tags"] += 1

        # file size
        filepath = meta.get("filepath", "")
        if filepath and os.path.isfile(filepath):
            stats["total_size_bytes"] += os.path.getsize(filepath)

    stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)

    return stats


def format_stats_table(stats: dict) -> str:
    """Turn stats dict into a readable string for terminal output."""
    lines = []
    lines.append("=== Collection Statistics ===")
    lines.append("")
    lines.append(f"  Total files:      {stats['total_files']}")
    lines.append(f"  Total size:       {stats['total_size_mb']} MB")
    lines.append(f"  Complete tags:    {stats['complete_tags']}")
    lines.append(f"  Incomplete tags:  {stats['incomplete_tags']}")
    lines.append("")

    lines.append("  Format Breakdown:")
    for fmt, count in sorted(stats["by_format"].items()):
        lines.append(f"    {fmt}: {count}")
    lines.append("")

    lines.append("  Genre Breakdown:")
    for genre, count in sorted(stats["by_genre"].items(), key=lambda x: x[1], reverse=True):
        lines.append(f"    {genre}: {count}")
    lines.append("")

    lines.append("  Top Artists:")
    sorted_artists = sorted(stats["by_artist"].items(), key=lambda x: x[1], reverse=True)
    for artist, count in sorted_artists[:10]:
        lines.append(f"    {artist}: {count}")

    return "\n".join(lines)
