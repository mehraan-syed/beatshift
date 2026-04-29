# Requirements — beatshift

## 1. Project Overview

beatshift is a cli tool for scanning, tagging, and organising local
music downloads. It's aimed at people who download music
(especially FLAC files) and end up with folders full of poorly named, untagged files.

Since a lot of my FLAC downloads come with inconsistent or missing metadata
I wanted a tool that could scan a folder, tell me what's tagged and what
isn't and when possible, fix the tags using an online database, and then sort
everything into a proper Artist/Album/Track folder structure.

---

## 2. Software Process Model

### Chosen Model: Incremental Development

### Planned Increments

| Increment | What It Adds                                             | Priority    |
| --------- | -------------------------------------------------------- | ----------- |
| 1         | Scan folders for audio files + read metadata + basic CLI | Must Have   |
| 2         | Organise files into Artist/Album/Track folders           | Must Have   |
| 3         | Show collection stats (file counts, genres, sizes)       | Should Have |
| 4         | Look up missing tags from MusicBrainz                    | Should Have |
| 5         | Find duplicate files + dry-run preview mode              | Could Have  |

---

## 3. Functional Requirements

These describe what the tool actually does.

| ID    | Requirement                                                                           | Priority    | Increment |
| ----- | ------------------------------------------------------------------------------------- | ----------- | --------- |
| FR-01 | Scan a folder (including subfolders) and find all FLAC, MP3, and WAV files            | Must Have   | 1         |
| FR-02 | Read metadata tags from audio files (title, artist, album, genre, year, track number) | Must Have   | 1         |
| FR-03 | Show a summary of which files have complete, partial, or missing tags                 | Must Have   | 1         |
| FR-04 | Move and rename files into an Artist/Album/Track folder structure                     | Must Have   | 2         |
| FR-05 | Support a --dry-run flag that shows what would happen without moving anything         | Should Have | 5         |
| FR-06 | Show collection stats — file count, format breakdown, genre distribution, total size  | Should Have | 3         |
| FR-07 | Query MusicBrainz to find suggested tags for files with missing metadata              | Should Have | 4         |
| FR-08 | Let the user accept, reject, or modify suggested tags before saving                   | Should Have | 4         |
| FR-09 | Detect potential duplicate files based on matching metadata                           | Could Have  | 5         |
| FR-10 | Show help text when the user runs --help                                              | Must Have   | 1         |

---

## 4. Non-Functional Requirements

These describe how the tool should behave, not what it does.

| ID     | Requirement                                                                    | Category        | Priority    |
| ------ | ------------------------------------------------------------------------------ | --------------- | ----------- |
| NFR-01 | Should handle a folder with 1,000 files in under 30 seconds                    | Performance     | Should Have |
| NFR-02 | Must work on Windows, macOS, and Linux                                         | Portability     | Must Have   |
| NFR-03 | Must never delete or overwrite files without the user confirming               | Safety          | Must Have   |
| NFR-04 | Must be installable with pip install from the project folder                   | Usability       | Must Have   |
| NFR-05 | Core modules should have unit tests with decent coverage                       | Testability     | Should Have |
| NFR-06 | Code should follow PEP 8 and have docstrings on public functions               | Maintainability | Should Have |
| NFR-07 | Should handle broken or corrupted audio files without crashing                 | Reliability     | Must Have   |
| NFR-08 | Must respect MusicBrainz rate limits (max 1 request per second)                | Compliance      | Must Have   |
| NFR-09 | Terminal output should use colour to distinguish errors, warnings, and success | Usability       | Could Have  |
| NFR-10 | Everything except MusicBrainz lookup should work fully offline                 | Availability    | Must Have   |

---

## 5. Traceability

This table maps each requirement to the code that implements it and the
test that verifies it.

| Requirement | Code Module       | Test                                      | Increment |
| ----------- | ----------------- | ----------------------------------------- | --------- |
| FR-01       | scanner.py        | test_scanner.py::test_recursive_scan      | 1         |
| FR-02       | tagger.py         | test_tagger.py::test_read_metadata        | 1         |
| FR-03       | cli.py, tagger.py | test_tagger.py::test_summary_report       | 1         |
| FR-04       | organizer.py      | test_organizer.py::test_organize_files    | 2         |
| FR-05       | organizer.py      | test_organizer.py::test_dry_run           | 5         |
| FR-06       | stats.py          | test_stats.py::test_collection_stats      | 3         |
| FR-07       | musicbrainz.py    | test_musicbrainz.py::test_api_lookup      | 4         |
| FR-08       | cli.py, tagger.py | test_tagger.py::test_user_confirmation    | 4         |
| FR-09       | scanner.py        | test_scanner.py::test_duplicate_detection | 5         |
| FR-10       | cli.py            | test_cli.py::test_help_flag               | 1         |
