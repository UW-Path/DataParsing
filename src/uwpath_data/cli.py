from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

from uwpath_data.artifacts import RawSnapshotWriter, RawTextSnapshotWriter, publish_catalog
from uwpath_data.comparison import compare_catalogs
from uwpath_data.sources.kuali import KualiAdapter, KualiSnapshotAdapter
from uwpath_data.sources.legacy_html import (
    LegacyBuildResult,
    LegacyHtmlAdapter,
    LegacyHtmlSnapshotAdapter,
)
from uwpath_data.verification import VerificationError, verify_catalog_directory

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


def add_backfill_arguments(parser: argparse.ArgumentParser) -> None:
    years = parser.add_mutually_exclusive_group(required=True)
    years.add_argument(
        "--year",
        action="append",
        dest="academic_years",
        type=academic_year,
        help="Academic year to backfill; repeat for multiple years",
    )
    years.add_argument(
        "--all-available",
        action="store_true",
        help="Backfill every academic year currently exposed by Kuali",
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
    replacement = parser.add_mutually_exclusive_group()
    replacement.add_argument(
        "--resume",
        action="store_true",
        help="Verify and skip releases that already exist",
    )
    replacement.add_argument(
        "--force",
        action="store_true",
        help="Replace existing releases after rebuilding them",
    )
    parser.add_argument(
        "--without-raw",
        action="store_true",
        help="Do not retain raw source responses (not recommended for published data)",
    )


def add_legacy_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "academic_year", type=academic_year, help="Academic year in YYYY-YYYY format"
    )
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument(
        "--subject",
        action="append",
        help="Course subject such as CS or MATH; repeat for multiple subjects",
    )
    scope.add_argument(
        "--full-catalog",
        action="store_true",
        help="Fetch every subject known to the legacy UWPath parser",
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


def progress_reporter(academic_year: str) -> Callable[[str], None]:
    def report(message: str) -> None:
        print(f"[{academic_year}] {message}", file=sys.stderr, flush=True)

    return report


def build_metadata(args: argparse.Namespace, *, retain_raw: bool) -> dict[str, Any]:
    return {
        "scope": "full_catalog" if args.full_catalog else "program_slice",
        "program_selectors": sorted(args.program or []),
        "raw_snapshot": retain_raw,
    }


def build_release(
    adapter: KualiAdapter,
    args: argparse.Namespace,
    academic_year: str,
    *,
    retain_raw: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    target = prepare_target(args.output, academic_year, args.force)
    args.output.mkdir(parents=True, exist_ok=True)
    staging_root = Path(tempfile.mkdtemp(prefix=f".{academic_year}.partial-", dir=args.output))
    try:
        staging_target = staging_root / academic_year
        raw_sink = RawSnapshotWriter(staging_target / "raw") if retain_raw else None
        selectors = None if args.full_catalog else args.program
        catalog = adapter.build_catalog(
            academic_year,
            selectors,
            workers=args.workers,
            max_courses=args.max_courses,
            raw_sink=raw_sink,
            progress=progress_reporter(academic_year),
        )
        manifest = publish_catalog(
            catalog,
            staging_root,
            build=build_metadata(args, retain_raw=retain_raw),
        )
        verification = verify_catalog_directory(staging_target)
        if not verification["publishable"]:
            raise VerificationError(f"Catalog {academic_year} failed the publishable release gate")
        replace_snapshot(staging_target, target)
        return manifest, verification
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)


def legacy_build_metadata(
    args: argparse.Namespace,
    result: LegacyBuildResult,
    *,
    retain_raw: bool,
) -> dict[str, Any]:
    return {
        "scope": "legacy_course_catalog" if args.full_catalog else "legacy_subject_slice",
        "subject_selectors": [] if args.full_catalog else list(result.requested_subjects),
        "fetched_subjects": list(result.fetched_subjects),
        "missing_subjects": list(result.missing_subjects),
        "empty_subjects": list(result.empty_subjects),
        "raw_snapshot": retain_raw,
    }


def build_legacy_release(
    adapter: LegacyHtmlAdapter,
    args: argparse.Namespace,
    *,
    retain_raw: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    target = prepare_target(args.output, args.academic_year, args.force)
    args.output.mkdir(parents=True, exist_ok=True)
    staging_root = Path(tempfile.mkdtemp(prefix=f".{args.academic_year}.partial-", dir=args.output))
    try:
        staging_target = staging_root / args.academic_year
        raw_sink = RawTextSnapshotWriter(staging_target / "raw") if retain_raw else None
        subjects = None if args.full_catalog else args.subject
        result = adapter.build_catalog(
            args.academic_year,
            subjects,
            workers=args.workers,
            max_courses=args.max_courses,
            raw_sink=raw_sink,
            progress=progress_reporter(args.academic_year),
        )
        manifest = publish_catalog(
            result.catalog,
            staging_root,
            build=legacy_build_metadata(args, result, retain_raw=retain_raw),
        )
        verification = verify_catalog_directory(staging_target)
        if not verification["publishable"]:
            raise VerificationError(
                f"Catalog {args.academic_year} failed the publishable release gate"
            )
        replace_snapshot(staging_target, target)
        return manifest, verification
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)


def resolve_backfill_years(
    adapter: KualiAdapter,
    requested_years: list[str] | None,
    all_available: bool,
) -> list[str]:
    available = set(adapter.available_years())
    selected = available if all_available else set(requested_years or [])
    missing = sorted(selected - available)
    if missing:
        raise ValueError("Kuali does not expose requested academic years: " + ", ".join(missing))
    return sorted(selected, reverse=True)


def run_backfill(adapter: KualiAdapter, args: argparse.Namespace) -> list[dict[str, Any]]:
    years = resolve_backfill_years(adapter, args.academic_years, args.all_available)
    results: list[dict[str, Any]] = []
    expected_build = build_metadata(args, retain_raw=not args.without_raw)
    for year in years:
        target = args.output / year
        if args.resume and target.exists() and not target.is_symlink():
            verification = verify_catalog_directory(target)
            if not verification["publishable"]:
                raise VerificationError(
                    f"Existing catalog {year} is not publishable; "
                    "use a different output directory or pass --force"
                )
            if verification.get("build") != expected_build:
                raise VerificationError(
                    f"Existing catalog {year} does not match the requested build scope; "
                    "use a different output directory or pass --force"
                )
            results.append({"status": "skipped", **verification})
            print(f"[{year}] existing release verified; skipping", file=sys.stderr)
            continue

        manifest, verification = build_release(
            adapter,
            args,
            year,
            retain_raw=not args.without_raw,
        )
        results.append(
            {
                "status": "published",
                **verification,
                "generated_at": manifest["generated_at"],
                "source_id": manifest["source_id"],
            }
        )
        print(f"[{year}] release verified and published", file=sys.stderr)
    return results


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

    backfill = subparsers.add_parser(
        "backfill-kuali", help="Build multiple Kuali catalog releases newest-to-oldest"
    )
    add_backfill_arguments(backfill)

    rebuild = subparsers.add_parser(
        "rebuild-kuali", help="Rebuild a catalog from a retained raw Kuali snapshot"
    )
    add_snapshot_arguments(rebuild)
    rebuild.add_argument("--raw", type=Path, required=True, help="Path to the raw snapshot root")

    legacy_snapshot = subparsers.add_parser(
        "snapshot-legacy-courses",
        help="Build a course catalog from Waterloo's static legacy HTML",
    )
    add_legacy_arguments(legacy_snapshot)
    legacy_snapshot.add_argument(
        "--without-raw",
        action="store_true",
        help="Do not retain raw HTML pages (not recommended for published data)",
    )

    legacy_rebuild = subparsers.add_parser(
        "rebuild-legacy-courses",
        help="Rebuild a legacy course catalog from retained raw HTML",
    )
    add_legacy_arguments(legacy_rebuild)
    legacy_rebuild.add_argument(
        "--raw", type=Path, required=True, help="Path to the raw legacy snapshot root"
    )

    verify = subparsers.add_parser(
        "verify-catalog", help="Verify a published catalog and its manifest"
    )
    verify.add_argument("catalog", type=Path, help="Catalog year directory")

    compare = subparsers.add_parser(
        "compare-catalogs", help="Compare a candidate catalog with a baseline"
    )
    compare.add_argument("baseline", type=Path)
    compare.add_argument("candidate", type=Path)
    compare.add_argument("--max-course-drop-percent", type=float, default=10)
    compare.add_argument("--max-program-drop-percent", type=float, default=10)
    compare.add_argument("--max-manual-rule-increase", type=int)
    compare.add_argument("--require-planner-ready", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.command in {"snapshot-legacy-courses", "rebuild-legacy-courses"}:
        if args.command == "rebuild-legacy-courses":
            target = args.output / args.academic_year
            raw_root = args.raw.resolve()
            if raw_root == target.resolve() or raw_root.is_relative_to(target.resolve()):
                raise SystemExit("The rebuild output would replace its input raw snapshot")
            legacy_adapter = LegacyHtmlSnapshotAdapter(args.raw)
        else:
            legacy_adapter = LegacyHtmlAdapter()
        try:
            manifest, _ = build_legacy_release(
                legacy_adapter,
                args,
                retain_raw=(args.command == "snapshot-legacy-courses" and not args.without_raw),
            )
        except (ValueError, VerificationError) as error:
            raise SystemExit(str(error)) from error
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return

    adapter = KualiAdapter()
    if args.command == "list-kuali-years":
        for year in adapter.available_years():
            print(year)
        return

    if args.command == "backfill-kuali":
        try:
            results = run_backfill(adapter, args)
        except (ValueError, VerificationError) as error:
            raise SystemExit(str(error)) from error
        print(json.dumps({"results": results}, indent=2, sort_keys=True))
        return

    try:
        if args.command == "verify-catalog":
            print(json.dumps(verify_catalog_directory(args.catalog), indent=2, sort_keys=True))
            return
        if args.command == "compare-catalogs":
            report = compare_catalogs(
                args.baseline,
                args.candidate,
                max_course_drop_percent=args.max_course_drop_percent,
                max_program_drop_percent=args.max_program_drop_percent,
                max_manual_rule_increase=args.max_manual_rule_increase,
                require_planner_ready=args.require_planner_ready,
            )
            print(json.dumps(report, indent=2, sort_keys=True))
            if not report["gates"]["passed"]:
                raise SystemExit(2)
            return
    except VerificationError as error:
        raise SystemExit(str(error)) from error

    if args.command == "rebuild-kuali":
        target = prepare_target(args.output, args.academic_year, args.force)
        raw_root = args.raw.resolve()
        if raw_root == target.resolve() or raw_root.is_relative_to(target.resolve()):
            raise SystemExit("The rebuild output would replace its input raw snapshot")
        adapter = KualiSnapshotAdapter(args.raw)
    manifest, _ = build_release(
        adapter,
        args,
        args.academic_year,
        retain_raw=args.command == "snapshot-kuali" and not args.without_raw,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
