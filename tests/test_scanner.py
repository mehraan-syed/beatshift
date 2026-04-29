"""Tests for the scanner module."""

import os
import tempfile
import pytest
from beatshift.scanner import scan_directory, find_duplicates, SUPPORTED_EXTENSIONS


class TestScanDirectory:
    """Tests for scan_directory function."""

    def test_finds_supported_files(self, tmp_path):
        """Should find FLAC, MP3, and WAV files."""
        # Create test files
        (tmp_path / "song.flac").write_bytes(b"fake")
        (tmp_path / "song.mp3").write_bytes(b"fake")
        (tmp_path / "song.wav").write_bytes(b"fake")

        result = scan_directory(str(tmp_path))

        assert len(result) == 3

    def test_ignores_unsupported_files(self, tmp_path):
        """Should ignore non-audio files like .txt and .jpg."""
        (tmp_path / "song.flac").write_bytes(b"fake")
        (tmp_path / "notes.txt").write_text("hello")
        (tmp_path / "cover.jpg").write_bytes(b"fake")

        result = scan_directory(str(tmp_path))

        assert len(result) == 1
        assert result[0].endswith(".flac")

    def test_recursive_scan(self, tmp_path):
        """Should find files in subdirectories."""
        sub = tmp_path / "artist" / "album"
        sub.mkdir(parents=True)
        (sub / "track.flac").write_bytes(b"fake")
        (tmp_path / "root_song.mp3").write_bytes(b"fake")

        result = scan_directory(str(tmp_path))

        assert len(result) == 2

    def test_returns_sorted_paths(self, tmp_path):
        """Results should be sorted alphabetically."""
        (tmp_path / "b_song.flac").write_bytes(b"fake")
        (tmp_path / "a_song.flac").write_bytes(b"fake")

        result = scan_directory(str(tmp_path))

        assert "a_song" in result[0]
        assert "b_song" in result[1]

    def test_empty_directory(self, tmp_path):
        """Should return empty list for directory with no audio files."""
        result = scan_directory(str(tmp_path))

        assert result == []

    def test_nonexistent_path_raises_error(self):
        """Should raise FileNotFoundError for invalid path."""
        with pytest.raises(FileNotFoundError):
            scan_directory("/nonexistent/path/12345")

    def test_file_path_raises_error(self, tmp_path):
        """Should raise NotADirectoryError if given a file instead."""
        f = tmp_path / "song.flac"
        f.write_bytes(b"fake")

        with pytest.raises(NotADirectoryError):
            scan_directory(str(f))

    def test_custom_extensions(self, tmp_path):
        """Should respect custom extension filter."""
        (tmp_path / "song.flac").write_bytes(b"fake")
        (tmp_path / "song.mp3").write_bytes(b"fake")

        result = scan_directory(str(tmp_path), extensions={".flac"})

        assert len(result) == 1
        assert result[0].endswith(".flac")

    def test_returns_absolute_paths(self, tmp_path):
        """All returned paths should be absolute."""
        (tmp_path / "song.flac").write_bytes(b"fake")

        result = scan_directory(str(tmp_path))

        assert os.path.isabs(result[0])


class TestFindDuplicates:
    """Tests for find_duplicates function."""

    def test_no_duplicates(self):
        """Should return empty list when no duplicates exist."""
        files = ["/music/one.flac", "/music/two.flac"]

        def mock_meta(f):
            if "one" in f:
                return {"title": "Song A", "artist": "Artist A", "album": "Album A"}
            return {"title": "Song B", "artist": "Artist B", "album": "Album B"}

        result = find_duplicates(files, metadata_fn=mock_meta)

        assert result == []

    def test_finds_duplicates(self):
        """Should detect files with identical metadata."""
        files = ["/music/one.flac", "/music/two.flac", "/music/unique.flac"]

        def mock_meta(f):
            if "unique" in f:
                return {"title": "Unique", "artist": "Other", "album": "Diff"}
            return {"title": "Same", "artist": "Same", "album": "Same"}

        result = find_duplicates(files, metadata_fn=mock_meta)

        assert len(result) == 1
        assert len(result[0]) == 2

    def test_no_metadata_fn_returns_empty(self):
        """Should return empty list if no metadata function is provided."""
        result = find_duplicates(["/music/one.flac", "/music/two.flac"])

        assert result == []
