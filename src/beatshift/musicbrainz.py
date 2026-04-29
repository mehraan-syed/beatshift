"""
MusicBrainz module — looks up song metadata from the
MusicBrainz online database. Used when files have missing tags.
"""

import time
from typing import Optional

import musicbrainzngs

# musicbrainz requires apps to identify themselves
musicbrainzngs.set_useragent(
    "beatshift",
    "1.0.0",
    "https://github.com/beatshift",
)

# for rate limiting — they allow max 1 request per second
_last_request_time = 0.0


def _rate_limit():
    """Wait if needed so we don't exceed 1 request per second."""
    global _last_request_time

    now = time.time()
    elapsed = now - _last_request_time

    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)

    _last_request_time = time.time()


def lookup_track(
    title: str = "",
    artist: str = "",
    album: str = "",
) -> Optional[dict]:
    """
    Search musicbrainz for a track. Uses whatever info we have
    (title, artist, album) to build the query. Returns the best
    match or None.
    """
    if not title and not artist:
        return None

    # build query from whatever fields we have
    query_parts = []
    if title:
        query_parts.append(f'recording:"{title}"')
    if artist:
        query_parts.append(f'artist:"{artist}"')
    if album:
        query_parts.append(f'release:"{album}"')

    query = " AND ".join(query_parts)

    try:
        _rate_limit()
        result = musicbrainzngs.search_recordings(query=query, limit=5)
    except Exception:
        return None

    recordings = result.get("recording-list", [])

    if not recordings:
        return None

    # take the top result
    top = recordings[0]

    suggested = {
        "title": top.get("title", ""),
        "artist": "",
        "album": "",
        "year": "",
        "track": "",
    }

    # dig into the nested response structure for artist info
    artist_credit = top.get("artist-credit", [])
    if artist_credit:
        suggested["artist"] = artist_credit[0].get("name", "")

    # get album and year from the first release
    release_list = top.get("release-list", [])
    if release_list:
        release = release_list[0]
        suggested["album"] = release.get("title", "")
        suggested["year"] = release.get("date", "")[:4]

        # try to get track number
        medium_list = release.get("medium-list", [])
        if medium_list:
            track_list = medium_list[0].get("track-list", [])
            if track_list:
                suggested["track"] = track_list[0].get("number", "")

    return suggested


def search_recordings(query: str, limit: int = 5) -> list:
    """General text search on musicbrainz. Returns simplified results."""
    try:
        _rate_limit()
        result = musicbrainzngs.search_recordings(query=query, limit=limit)
    except Exception:
        return []

    results = []

    for rec in result.get("recording-list", []):
        entry = {
            "title": rec.get("title", ""),
            "artist": "",
            "album": "",
        }

        artist_credit = rec.get("artist-credit", [])
        if artist_credit:
            entry["artist"] = artist_credit[0].get("name", "")

        release_list = rec.get("release-list", [])
        if release_list:
            entry["album"] = release_list[0].get("title", "")

        results.append(entry)

    return results
