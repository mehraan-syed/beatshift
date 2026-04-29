# System Modelling — beatshift

## 1. Architecture

beatshift uses a modular design where each job (scanning, reading tags,
organising files, showing stats) is handled by its own module.
Each module can be built and tested on its own, which fits the incremental development plan.
If I want to add a new feature later, I just add a new module without touching the existing ones.
Bugs are easier to track down when each file has one job.

---

## 2. Component Diagram

High-level view of how the parts connect.

```mermaid
graph TD
    A[User] -->|runs command| B[cli.py]
    B -->|scan command| C[scanner.py]
    B -->|tag command| D[tagger.py]
    B -->|organize command| E[organizer.py]
    B -->|stats command| F[stats.py]
    B -->|lookup command| G[musicbrainz.py]

    C -->|file list| D
    C -->|file list| F
    D -->|metadata| E
    D -->|metadata| F
    G -->|suggested tags| D

    H[(Local Audio Files)] -->|read| C
    I[(MusicBrainz API)] -->|query| G
    E -->|move/rename| H
```

---

## 3. Class Diagram

Shows what functions each module has and how they depend on each other.

```mermaid
classDiagram
    class CLI {
        +main()
        +parse_args() Namespace
        -_handle_scan(args)
        -_handle_organize(args)
        -_handle_stats(args)
        -_handle_lookup(args)
    }

    class Scanner {
        +scan_directory(path: str, extensions: list) list~AudioFile~
        +find_duplicates(files: list) list~tuple~
        -_is_audio_file(filepath: str) bool
    }

    class Tagger {
        +read_metadata(filepath: str) dict
        +write_metadata(filepath: str, metadata: dict) bool
        +get_metadata_summary(files: list) dict
        -_extract_flac(filepath: str) dict
        -_extract_mp3(filepath: str) dict
    }

    class Organizer {
        +organize_files(files: list, dest: str, pattern: str, dry_run: bool) list
        +build_new_path(metadata: dict, dest: str, pattern: str) str
        -_safe_move(src: str, dest: str) bool
    }

    class Stats {
        +collection_stats(files: list) dict
        +format_stats_table(stats: dict) str
        -_count_by_field(files: list, field: str) dict
        -_total_size(files: list) int
    }

    class MusicBrainzClient {
        +lookup_track(title: str, artist: str) dict
        +search_by_fingerprint(filepath: str) dict
        -_rate_limit() None
    }

    CLI --> Scanner : uses
    CLI --> Tagger : uses
    CLI --> Organizer : uses
    CLI --> Stats : uses
    CLI --> MusicBrainzClient : uses
    Scanner --> Tagger : passes files to
    MusicBrainzClient --> Tagger : provides tags to
    Tagger --> Organizer : provides metadata to
    Scanner --> Stats : provides files to
```

---

## 4. Sequence Diagram — Scan and Organise

What happens when someone runs `beatshift organize /music --dry-run`.

```mermaid
sequenceDiagram
    actor User
    participant CLI as cli.py
    participant Scanner as scanner.py
    participant Tagger as tagger.py
    participant Organizer as organizer.py

    User->>CLI: beatshift organize /music --dry-run
    CLI->>Scanner: scan_directory("/music")
    Scanner->>Scanner: Walk directory tree
    Scanner-->>CLI: List of audio file paths

    loop For each audio file
        CLI->>Tagger: read_metadata(filepath)
        Tagger-->>CLI: metadata dict
    end

    CLI->>Organizer: organize_files(files, dest, pattern, dry_run=True)

    loop For each file
        Organizer->>Organizer: build_new_path(metadata)
        Organizer-->>CLI: Preview: old_path → new_path
    end

    CLI-->>User: Display preview table (no files moved)
```

---

## 5. Sequence Diagram — MusicBrainz Lookup

What happens when someone runs `beatshift lookup /music/unknown.flac`.

```mermaid
sequenceDiagram
    actor User
    participant CLI as cli.py
    participant Tagger as tagger.py
    participant MB as musicbrainz.py
    participant API as MusicBrainz API

    User->>CLI: beatshift lookup /music/unknown.flac
    CLI->>Tagger: read_metadata(filepath)
    Tagger-->>CLI: {title: "Unknown", artist: ""}

    CLI->>MB: lookup_track(title, artist)
    MB->>MB: _rate_limit()
    MB->>API: GET search/recording?query=...
    API-->>MB: JSON response with matches
    MB-->>CLI: {title: "Blinding Lights", artist: "The Weeknd", album: "After Hours"}

    CLI-->>User: Display suggested tags
    User->>CLI: Accept / Reject / Modify

    alt User accepts
        CLI->>Tagger: write_metadata(filepath, new_tags)
        Tagger-->>CLI: Success
        CLI-->>User: Tags updated
    else User rejects
        CLI-->>User: No changes made
    end
```

---

## 6. Activity Diagram — Main Flow

Overall flowchart of what the app does depending on the command.

```mermaid
flowchart TD
    A([Start]) --> B[Parse CLI arguments]
    B --> C{Which command?}

    C -->|scan| D[Scan directory for audio files]
    D --> E[Read metadata for each file]
    E --> F[Display summary report]
    F --> Z([End])

    C -->|organize| G[Scan directory for audio files]
    G --> H[Read metadata for each file]
    H --> I{--dry-run flag?}
    I -->|Yes| J[Preview file moves]
    J --> Z
    I -->|No| K[Move and rename files]
    K --> L[Display results]
    L --> Z

    C -->|stats| M[Scan directory for audio files]
    M --> N[Calculate stats]
    N --> O[Display stats table]
    O --> Z

    C -->|lookup| P[Read metadata from file]
    P --> Q[Query MusicBrainz API]
    Q --> R{Results found?}
    R -->|Yes| S[Show suggested tags]
    S --> T{User accepts?}
    T -->|Yes| U[Write new metadata]
    U --> Z
    T -->|No| Z
    R -->|No| V[Show no results message]
    V --> Z
```

---

## 7. Design Decisions

| Decision                    | Why                                                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Modular architecture        | Each module does one thing. Easier to test, easier to debug, fits incremental development.                               |
| mutagen for metadata        | Handles both FLAC and MP3 through one library. Well documented, widely used.                                             |
| MusicBrainz over other APIs | Free, no API key needed, open source. Fits the assignment constraint of no costs.                                        |
| rich for terminal output    | Gives colour and tables with very little code. Makes the output actually readable.                                       |
| Configurable folder pattern | Users might want different structures. Using `{artist}/{album}/{track} - {title}` as default but letting them change it. |
| Dry-run as a safety feature | Moving files is permanent. Letting users preview first prevents accidents. Directly tied to NFR-03.                      |
