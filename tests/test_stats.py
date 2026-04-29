"""Tests for the stats module."""

from beatshift.stats import collection_stats, format_stats_table


class TestCollectionStats:
    """Tests for collection_stats function."""

    def test_empty_collection(self):
        """Should handle empty file list."""
        result = collection_stats([])

        assert result["total_files"] == 0
        assert result["by_format"] == {}
        assert result["total_size_bytes"] == 0

    def test_counts_formats(self):
        """Should correctly count files by format."""
        files = [
            {"format": "FLAC", "genre": "Rock", "artist": "A", "status": "complete", "filepath": ""},
            {"format": "FLAC", "genre": "Rock", "artist": "A", "status": "complete", "filepath": ""},
            {"format": "MP3", "genre": "Pop", "artist": "B", "status": "complete", "filepath": ""},
        ]

        result = collection_stats(files)

        assert result["by_format"]["FLAC"] == 2
        assert result["by_format"]["MP3"] == 1

    def test_counts_genres(self):
        """Should correctly count files by genre."""
        files = [
            {"format": "FLAC", "genre": "Rock", "artist": "A", "status": "complete", "filepath": ""},
            {"format": "FLAC", "genre": "Rock", "artist": "A", "status": "complete", "filepath": ""},
            {"format": "FLAC", "genre": "Jazz", "artist": "B", "status": "complete", "filepath": ""},
        ]

        result = collection_stats(files)

        assert result["by_genre"]["Rock"] == 2
        assert result["by_genre"]["Jazz"] == 1

    def test_empty_genre_counted_as_unknown(self):
        """Should count files with no genre as 'Unknown'."""
        files = [
            {"format": "FLAC", "genre": "", "artist": "A", "status": "complete", "filepath": ""},
        ]

        result = collection_stats(files)

        assert result["by_genre"]["Unknown"] == 1

    def test_tag_completeness(self):
        """Should count complete and incomplete tags."""
        files = [
            {"format": "FLAC", "genre": "Rock", "artist": "A", "status": "complete", "filepath": ""},
            {"format": "MP3", "genre": "", "artist": "", "status": "missing", "filepath": ""},
        ]

        result = collection_stats(files)

        assert result["complete_tags"] == 1
        assert result["incomplete_tags"] == 1

    def test_total_files_count(self):
        """Should correctly count total files."""
        files = [
            {"format": "FLAC", "genre": "", "artist": "", "status": "missing", "filepath": ""},
            {"format": "MP3", "genre": "", "artist": "", "status": "missing", "filepath": ""},
            {"format": "WAV", "genre": "", "artist": "", "status": "missing", "filepath": ""},
        ]

        result = collection_stats(files)

        assert result["total_files"] == 3


class TestFormatStatsTable:
    """Tests for format_stats_table function."""

    def test_returns_string(self):
        """Should return a formatted string."""
        stats = {
            "total_files": 1,
            "total_size_mb": 5.0,
            "complete_tags": 1,
            "incomplete_tags": 0,
            "by_format": {"FLAC": 1},
            "by_genre": {"Rock": 1},
            "by_artist": {"Artist": 1},
        }

        result = format_stats_table(stats)

        assert isinstance(result, str)
        assert "Collection Statistics" in result

    def test_contains_format_info(self):
        """Should include format breakdown."""
        stats = {
            "total_files": 1,
            "total_size_mb": 5.0,
            "complete_tags": 1,
            "incomplete_tags": 0,
            "by_format": {"FLAC": 1},
            "by_genre": {},
            "by_artist": {},
        }

        result = format_stats_table(stats)

        assert "FLAC" in result
