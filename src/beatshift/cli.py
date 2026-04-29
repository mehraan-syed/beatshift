"""
CLI module — the main entry point. Handles commands and
calls the other modules.
"""

import argparse
import os
import sys

from rich.console import Console
from rich.table import Table

from beatshift.scanner import scan_directory, find_duplicates
from beatshift.tagger import read_metadata, get_metadata_summary, write_metadata
from beatshift.organizer import organize_files
from beatshift.stats import collection_stats, format_stats_table
from beatshift.musicbrainz import lookup_track

console = Console()


def main():
    """Entry point — parse args and run the right command."""
    parser = argparse.ArgumentParser(
        prog="beatshift",
        description="Scan, tag, and organise your music collection.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan
    scan_parser = subparsers.add_parser("scan", help="Scan a directory for audio files")
    scan_parser.add_argument("path", help="Directory to scan")

    # organize
    org_parser = subparsers.add_parser("organize", help="Organise files into folder structure")
    org_parser.add_argument("path", help="Directory containing audio files")
    org_parser.add_argument("--dest", default=None, help="Destination directory (default: same as source)")
    org_parser.add_argument("--pattern", default=None, help="Folder pattern e.g. {artist}/{album}/{track} - {title}")
    org_parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")

    # stats
    stats_parser = subparsers.add_parser("stats", help="Display collection statistics")
    stats_parser.add_argument("path", help="Directory to analyse")

    # lookup
    lookup_parser = subparsers.add_parser("lookup", help="Look up metadata from MusicBrainz")
    lookup_parser.add_argument("path", help="Path to an audio file")
    lookup_parser.add_argument("--apply", action="store_true", help="Apply suggested tags without prompting")

    # duplicates
    dup_parser = subparsers.add_parser("duplicates", help="Find potential duplicate files")
    dup_parser.add_argument("path", help="Directory to check for duplicates")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "scan":
        _handle_scan(args)
    elif args.command == "organize":
        _handle_organize(args)
    elif args.command == "stats":
        _handle_stats(args)
    elif args.command == "lookup":
        _handle_lookup(args)
    elif args.command == "duplicates":
        _handle_duplicates(args)


def _handle_scan(args):
    """Scan a folder and show metadata summary."""
    try:
        files = scan_directory(args.path)
    except (FileNotFoundError, NotADirectoryError) as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    if not files:
        console.print("[yellow]No audio files found.[/yellow]")
        return

    summary = get_metadata_summary(files)

    console.print(f"\n[bold]Scanned {summary['total']} files[/bold]")
    console.print(f"  [green]Complete:[/green]  {summary['complete']}")
    console.print(f"  [yellow]Partial:[/yellow]   {summary['partial']}")
    console.print(f"  [red]Missing:[/red]   {summary['missing']}\n")

    table = Table(title="File Summary")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Artist", style="white")
    table.add_column("Title", style="white")
    table.add_column("Album", style="white")
    table.add_column("Status", style="bold")

    for f in summary["files"]:
        filename = os.path.basename(f["filepath"])
        status_colour = {
            "complete": "[green]complete[/green]",
            "partial": "[yellow]partial[/yellow]",
            "missing": "[red]missing[/red]",
        }
        table.add_row(
            filename,
            f.get("artist", "") or "-",
            f.get("title", "") or "-",
            f.get("album", "") or "-",
            status_colour.get(f["status"], f["status"]),
        )

    console.print(table)


def _handle_organize(args):
    """Organise files into folders based on metadata."""
    try:
        files = scan_directory(args.path)
    except (FileNotFoundError, NotADirectoryError) as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    if not files:
        console.print("[yellow]No audio files found.[/yellow]")
        return

    dest = args.dest if args.dest else args.path
    files_metadata = [read_metadata(f) for f in files]

    results = organize_files(
        files_metadata=files_metadata,
        dest=dest,
        pattern=args.pattern,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        console.print("\n[bold yellow]DRY RUN — no files will be moved[/bold yellow]\n")

    table = Table(title="Organise Results")
    table.add_column("Source", style="cyan")
    table.add_column("Destination", style="green")
    table.add_column("Status", style="bold")

    for r in results:
        src_name = os.path.basename(r["src"]) if r["src"] else "?"
        dest_name = r["dest"] if r["dest"] else "-"
        status_style = {
            "preview": "[yellow]preview[/yellow]",
            "moved": "[green]moved[/green]",
            "skipped": "[dim]skipped[/dim]",
            "failed": "[red]failed[/red]",
        }
        table.add_row(
            src_name,
            dest_name,
            status_style.get(r["status"], r["status"]),
        )

    console.print(table)


def _handle_stats(args):
    """Show collection stats."""
    try:
        files = scan_directory(args.path)
    except (FileNotFoundError, NotADirectoryError) as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    if not files:
        console.print("[yellow]No audio files found.[/yellow]")
        return

    files_metadata = [read_metadata(f) for f in files]

    # need the status field for stats to work
    summary = get_metadata_summary(files)
    meta_with_status = summary["files"]

    stats = collection_stats(meta_with_status)
    output = format_stats_table(stats)
    console.print(f"\n{output}\n")


def _handle_lookup(args):
    """Look up missing tags from MusicBrainz."""
    if not args.path:
        console.print("[red]Error:[/red] Please provide a file path.")
        sys.exit(1)

    meta = read_metadata(args.path)
    console.print(f"\n[bold]Current tags for:[/bold] {args.path}")
    console.print(f"  Title:  {meta.get('title') or '[dim]empty[/dim]'}")
    console.print(f"  Artist: {meta.get('artist') or '[dim]empty[/dim]'}")
    console.print(f"  Album:  {meta.get('album') or '[dim]empty[/dim]'}")
    console.print(f"  Genre:  {meta.get('genre') or '[dim]empty[/dim]'}")
    console.print(f"  Year:   {meta.get('year') or '[dim]empty[/dim]'}")

    console.print("\n[bold]Searching MusicBrainz...[/bold]")

    suggested = lookup_track(
        title=meta.get("title", ""),
        artist=meta.get("artist", ""),
        album=meta.get("album", ""),
    )

    if not suggested:
        console.print("[yellow]No matches found on MusicBrainz.[/yellow]")
        return

    console.print("\n[bold green]Suggested tags:[/bold green]")
    console.print(f"  Title:  {suggested.get('title', '')}")
    console.print(f"  Artist: {suggested.get('artist', '')}")
    console.print(f"  Album:  {suggested.get('album', '')}")
    console.print(f"  Year:   {suggested.get('year', '')}")
    console.print(f"  Track:  {suggested.get('track', '')}")

    if args.apply:
        write_metadata(args.path, suggested)
        console.print("\n[green]Tags applied.[/green]")
    else:
        console.print("")
        choice = input("Apply these tags? (y/n): ").strip().lower()
        if choice == "y":
            write_metadata(args.path, suggested)
            console.print("[green]Tags applied.[/green]")
        else:
            console.print("[dim]No changes made.[/dim]")


def _handle_duplicates(args):
    """Find potential duplicate files."""
    try:
        files = scan_directory(args.path)
    except (FileNotFoundError, NotADirectoryError) as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    if not files:
        console.print("[yellow]No audio files found.[/yellow]")
        return

    console.print(f"\n[bold]Checking {len(files)} files for duplicates...[/bold]\n")

    duplicates = find_duplicates(files, metadata_fn=read_metadata)

    if not duplicates:
        console.print("[green]No duplicates found.[/green]")
        return

    console.print(f"[yellow]Found {len(duplicates)} potential duplicate group(s):[/yellow]\n")

    for i, group in enumerate(duplicates, 1):
        console.print(f"  [bold]Group {i}:[/bold]")
        for filepath in group:
            console.print(f"    - {filepath}")
        console.print("")


if __name__ == "__main__":
    main()
