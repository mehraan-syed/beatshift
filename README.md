# beatshift

A cli tool for scanning, tagging, and organising local music collections.

---

## About

I built beatshift because I download a lot of FLAC music and most downloads have no tags, inconsistent naming,
everything dumped in one directory. This tool scans a music folder, reads the metadata from each
file, reports on what's tagged and what isn't, and can organise everything into
a clean Artist/Album/Track folder structure.

It can also look up missing tags using the MusicBrainz online database and
detect potential duplicate files.

---

## Features

- Scan folders recursively for FLAC, MP3, and WAV files
- Read metadata and show which files have complete, partial, or missing tags
- Organise files into `Artist/Album/Track - Title` folder structure
- Dry-run mode to preview changes before moving anything
- Collection stats — format breakdown, genre counts, file sizes
- MusicBrainz integration for looking up missing metadata
- Duplicate detection based on metadata matching
- Colour-coded terminal output

---

## Tech Stack

- **Language:** Python 3.9+
- **Metadata:** [mutagen](https://mutagen.readthedocs.io/)
- **Music Database:** [musicbrainzngs](https://python-musicbrainzngs.readthedocs.io/)
- **Terminal Output:** [rich](https://rich.readthedocs.io/)
- **Testing:** [pytest](https://docs.pytest.org/)
- **Packaging:** pyproject.toml (PEP 621)

---

## Setup

### Requirements

- Python 3.9+
- pip

### Install

```bash
# Clone the repo
git clone <repository-url>
cd beatshift

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# Install
Clone the repo, set up a virtual environment, and install:

    git clone <repository-url>
    cd beatshift
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"

On Windows use `.venv\Scripts\activate` instead.

### Check it works

    beatshift --help

---

## How to Use

### Scan a folder

    beatshift scan ~/Music

Shows every audio file found and whether its metadata is complete, partial, or missing.

### Organise files

    # Preview first
    beatshift organize ~/Music --dry-run

    # Actually organise
    beatshift organize ~/Music

    # Put organised files somewhere else
    beatshift organize ~/Music --dest ~/Music-Sorted

### View stats

    beatshift stats ~/Music

### Look up missing tags

    # Interactive — asks before applying
    beatshift lookup ~/Music/unknown_track.flac

    # Auto-apply
    beatshift lookup ~/Music/unknown_track.flac --apply

### Find duplicates

    beatshift duplicates ~/Music

---

## Project Structure

    beatshift/
    ├── src/beatshift/
    │   ├── __init__.py          # Version info
    │   ├── cli.py               # Command-line interface
    │   ├── scanner.py           # Finds audio files
    │   ├── tagger.py            # Reads/writes metadata
    │   ├── organizer.py         # Moves and renames files
    │   ├── stats.py             # Collection statistics
    │   └── musicbrainz.py       # MusicBrainz API client
    ├── tests/
    │   ├── test_scanner.py
    │   ├── test_tagger.py
    │   ├── test_organizer.py
    │   └── test_stats.py
    ├── pyproject.toml
    ├── Requirements.md
    ├── SystemModelling.md
    ├── CHANGELOG.md
    └── AI_REFLECTION.md

---

## Design Choices

**Why mutagen?** It handles both FLAC and MP3 metadata through one library,
so I didn't need separate tools for each format.

**Why MusicBrainz?** It's free, open source, and doesn't need an API key.
Other music databases either cost money or require registration.

**Why dry-run mode?** Moving and renaming files is permanent. I wanted a way
to see what would happen first before committing to it.

---

## Running Tests

    pytest tests/ -v

    pytest tests/ -v --cov=beatshift --cov-report=term-missing

---

## AI Usage

Some parts of this project were developed with help from ChatGPT(OpenAI). All AI-generated content was reviewed, tested, and modified where needed. Full details are in AI_REFLECTION.md.
```
