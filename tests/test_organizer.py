"""Tests for the organizer module."""

import os
import pytest
from beatshift.organizer import organize_files, build_new_path, _sanitize


class TestBuildNewPath:
    """Tests for build_new_path function."""

    def test_basic_path_building(self):
        """Should build correct path from metadata."""
        meta = {
            "artist": "The Weeknd",
            "album": "After Hours",
            "title": "Blinding Lights",
            "track": "9",
            "filepath": "/music/song.flac",
        }

        result = build_new_path(meta, "/output", "{artist}/{album}/{track} - {title}")

        # normalise so test works on both windows and linux
        assert os.path.normpath(result) == os.path.normpath("/output/The Weeknd/After Hours/09 - Blinding Lights.flac")



    def test_missing_artist_returns_empty(self):
        """Should return empty string if artist is missing."""
        meta = {
            "artist": "",
            "album": "Album",
            "title": "Song",
            "track": "1",
            "filepath": "/music/song.flac",
        }

        result = build_new_path(meta, "/output", "{artist}/{album}/{track} - {title}")

        assert result == ""

    def test_missing_title_returns_empty(self):
        """Should return empty string if title is missing."""
        meta = {
            "artist": "Artist",
            "album": "Album",
            "title": "",
            "track": "1",
            "filepath": "/music/song.flac",
        }

        result = build_new_path(meta, "/output", "{artist}/{album}/{track} - {title}")

        assert result == ""

    def test_missing_album_uses_default(self):
        """Should use 'Unknown Album' when album is missing."""
        meta = {
            "artist": "Artist",
            "album": "",
            "title": "Song",
            "track": "1",
            "filepath": "/music/song.mp3",
        }

        result = build_new_path(meta, "/output", "{artist}/{album}/{track} - {title}")

        assert "Unknown Album" in result

    def test_track_number_padding(self):
        """Should pad single-digit track numbers to 2 digits."""
        meta = {
            "artist": "Artist",
            "album": "Album",
            "title": "Song",
            "track": "3",
            "filepath": "/music/song.flac",
        }

        result = build_new_path(meta, "/output", "{artist}/{album}/{track} - {title}")

        assert "/03 - " in result

    def test_track_fraction_format(self):
        """Should handle track formats like '3/12'."""
        meta = {
            "artist": "Artist",
            "album": "Album",
            "title": "Song",
            "track": "3/12",
            "filepath": "/music/song.flac",
        }

        result = build_new_path(meta, "/output", "{artist}/{album}/{track} - {title}")

        assert "/03 - " in result


class TestSanitize:
    """Tests for _sanitize function."""

    def test_removes_illegal_characters(self):
        """Should remove characters illegal in file names."""
        result = _sanitize('Song: "The Best" <v2>')

        assert ":" not in result
        assert '"' not in result
        assert "<" not in result
        assert ">" not in result

    def test_strips_whitespace(self):
        """Should strip leading and trailing whitespace."""
        result = _sanitize("  Song Title  ")

        assert result == "Song Title"

    def test_empty_string(self):
        """Should handle empty string."""
        result = _sanitize("")

        assert result == ""

    def test_collapses_multiple_spaces(self):
        """Should replace multiple spaces with single space."""
        result = _sanitize("Song    Title")

        assert result == "Song Title"


class TestOrganizeFiles:
    """Tests for organize_files function."""

    def test_dry_run_does_not_move(self, tmp_path):
        """Dry run should preview without moving files."""
        f = tmp_path / "song.flac"
        f.write_bytes(b"fake")

        meta = [{
            "filepath": str(f),
            "artist": "Artist",
            "album": "Album",
            "title": "Song",
            "track": "1",
        }]

        results = organize_files(meta, str(tmp_path / "output"), dry_run=True)

        assert results[0]["status"] == "preview"
        assert f.exists()  # File should still be in original location

    def test_skips_missing_metadata(self):
        """Should skip files with insufficient metadata."""
        meta = [{
            "filepath": "/fake/song.flac",
            "artist": "",
            "album": "",
            "title": "",
            "track": "",
        }]

        results = organize_files(meta, "/output", dry_run=True)

        assert results[0]["status"] == "skipped"
