"""Tests for the tagger module."""

import os
import pytest
from beatshift.tagger import read_metadata, get_metadata_summary, REQUIRED_FIELDS


class TestReadMetadata:
    """Tests for read_metadata function."""

    def test_nonexistent_file_raises_error(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            read_metadata("/nonexistent/file.flac")

    def test_returns_dict_with_required_keys(self, tmp_path):
        """Should return dict with all expected keys even for empty wav."""
        f = tmp_path / "test.wav"
        f.write_bytes(b"RIFF" + b"\x00" * 100)

        result = read_metadata(str(f))

        assert "title" in result
        assert "artist" in result
        assert "album" in result
        assert "filepath" in result
        assert "format" in result

    def test_format_detection(self, tmp_path):
        """Should correctly identify file format."""
        f = tmp_path / "test.wav"
        f.write_bytes(b"RIFF" + b"\x00" * 100)

        result = read_metadata(str(f))

        assert result["format"] == "WAV"

    def test_filepath_is_absolute(self, tmp_path):
        """Returned filepath should be absolute."""
        f = tmp_path / "test.wav"
        f.write_bytes(b"RIFF" + b"\x00" * 100)

        result = read_metadata(str(f))

        assert os.path.isabs(result["filepath"])

    def test_unsupported_format_raises_error(self, tmp_path):
        """Should set error field for unsupported format."""
        f = tmp_path / "test.ogg"
        f.write_bytes(b"fake")

        result = read_metadata(str(f))

        assert "_error" in result


class TestGetMetadataSummary:
    """Tests for get_metadata_summary function."""

    def test_empty_list(self):
        """Should handle empty file list."""
        result = get_metadata_summary([])

        assert result["total"] == 0
        assert result["complete"] == 0
        assert result["partial"] == 0
        assert result["missing"] == 0

    def test_counts_are_correct(self, tmp_path):
        """Total should equal complete + partial + missing."""
        # Create some wav files (will have missing metadata)
        for i in range(3):
            f = tmp_path / f"test{i}.wav"
            f.write_bytes(b"RIFF" + b"\x00" * 100)

        files = [str(tmp_path / f"test{i}.wav") for i in range(3)]
        result = get_metadata_summary(files)

        assert result["total"] == 3
        total = result["complete"] + result["partial"] + result["missing"]
        assert total == result["total"]
