from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import uuid
from pathlib import Path

from uwpath_data.artifacts import RawSnapshotWriter, publish_catalog
from uwpath_data.sources.kuali import KualiAdapter, KualiSnapshotAdapter

ACADEMIC_YEAR_RE = re.compile(r"^(\d{4})-(\d{4})$")


def academic_year(value: str) -> str:
    match = ACADEMIC_YEAR_RE.fullmatch(value)
    if not match or int(match.group(2)) != int(match.group(1)) + 1:
        raise argparse.ArgumentTypeError("academic year must look like 2026-2027")
    return value


def add_snapshot_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "academic_year", type=academic_year, help="Academic year in YYYY-YYYY format"
    )
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument(
        "--program",
        action="append",
        help="Program code/title/pid or unique title fragment; repeat for multiple programs",
    )
    scope.add_argument(
        "--full-catalog",
        action="store_true",
        help="Fetch every program and every active course",
    )
    parser.add_argument("--output", type=Path, default=Path("dist/catalogs"))
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-courses", type=int, default=5000)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing snapshot for this academic year",
    )


def prepare_target(output: Path, year: str, force: bool) -> Path:
    target = output / year
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise SystemExit(f"Snapshot target must be a directory: {target}")
    if target.exists() and not force:
        raise SystemExit(f"Snapshot already exists at {target}; pass --force to replace it")
    return target


def replace_snapshot(staged: Path, target: Path) -> None:
    backup: Path | None = None
    if target.exists():
        backup = target.with_name(f".{target.name}.backup-{uuid.uuid4().hex}")
        target.replace(backup)
    try:
        staged.replace(target)
    except Exception:
        if backup is not None:
            backup.replace(target)
        raise
    if backup is not None:
        shutil.rmtree(backup)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="uwpath-data")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "list-kuali-years", help="List discoverable undergraduate Kuali calendars"
    )

    snapshot = subparsers.add_parser(
        "snapshot-kuali", help="Build a versioned catalog slice from Kuali"
    )
    add_snapshot_arguments(snapshot)
    snapshot.add_argument(
        "--without-raw",
        action="store_true",
        help="Do not retain raw source responses (not recommended for published data)",
    )

    rebuild = subparsers.add_parser(
        "rebuild-kuali", help="Rebuild a catalog from a retained raw Kuali snapshot"
    )
    add_snapshot_arguments(rebuild)
    rebuild.add_argument("--raw", type=Path, required=True, help="Path to the raw snapshot root")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    adapter = KualiAdapter()
    if args.command == "list-kuali-years":
        for year in adapter.available_years():
            print(year)
        return

    target = prepare_target(args.output, args.academic_year, args.force)
    if args.command == "rebuild-kuali":
        raw_root = args.raw.resolve()
        if raw_root == target.resolve() or raw_root.is_relative_to(target.resolve()):
            raise SystemExit("The rebuild output would replace its input raw snapshot")
        adapter = KualiSnapshotAdapter(args.raw)
    args.output.mkdir(parents=True, exist_ok=True)
    staging_root = Path(tempfile.mkdtemp(prefix=f".{args.academic_year}.partial-", dir=args.output))
    try:
        staging_target = staging_root / args.academic_year
        raw_sink = None
        if args.command == "snapshot-kuali" and not args.without_raw:
            raw_sink = RawSnapshotWriter(staging_target / "raw")
        selectors = None if args.full_catalog else args.program
        catalog = adapter.build_catalog(
            args.academic_year,
            selectors,
            workers=args.workers,
            max_courses=args.max_courses,
            raw_sink=raw_sink,
        )
        manifest = publish_catalog(catalog, staging_root)
        replace_snapshot(staging_target, target)
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
