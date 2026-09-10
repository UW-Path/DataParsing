import argparse
from pathlib import Path

import pytest

import uwpath_data.cli as cli
from uwpath_data.cli import (
    academic_year,
    build_metadata,
    build_release,
    prepare_target,
    replace_snapshot,
    resolve_backfill_years,
    run_backfill,
)
from uwpath_data.verification import VerificationError


class FakeAdapter:
    def __init__(self, years: list[str]) -> None:
        self.years = years

    def available_years(self) -> list[str]:
        return self.years

    def build_catalog(self, *args, **kwargs):
        return object()


def test_academic_year_rejects_invalid_or_nonconsecutive_years() -> None:
    assert academic_year("2026-2027") == "2026-2027"
    with pytest.raises(argparse.ArgumentTypeError):
        academic_year("../../tmp")
    with pytest.raises(argparse.ArgumentTypeError):
        academic_year("2026-2028")


def test_existing_snapshot_is_preserved_until_replacement(tmp_path: Path) -> None:
    target = tmp_path / "catalogs/2026-2027"
    target.mkdir(parents=True)
    (target / "old.json").write_text("old")

    with pytest.raises(SystemExit, match="pass --force"):
        prepare_target(tmp_path / "catalogs", "2026-2027", force=False)

    assert prepare_target(tmp_path / "catalogs", "2026-2027", force=True) == target
    assert (target / "old.json").read_text() == "old"

    staged = tmp_path / "staged"
    staged.mkdir()
    (staged / "new.json").write_text("new")
    replace_snapshot(staged, target)

    assert not (target / "old.json").exists()
    assert (target / "new.json").read_text() == "new"


def test_backfill_years_are_validated_and_ordered_newest_first() -> None:
    adapter = FakeAdapter(["2024-2025", "2026-2027", "2025-2026"])

    assert resolve_backfill_years(adapter, None, all_available=True) == [
        "2026-2027",
        "2025-2026",
        "2024-2025",
    ]
    assert resolve_backfill_years(
        adapter,
        ["2024-2025", "2026-2027", "2024-2025"],
        all_available=False,
    ) == ["2026-2027", "2024-2025"]

    with pytest.raises(ValueError, match="does not expose"):
        resolve_backfill_years(adapter, ["2023-2024"], all_available=False)


def test_build_metadata_distinguishes_full_catalogs_from_program_slices() -> None:
    full = argparse.Namespace(full_catalog=True, program=None)
    slice_args = argparse.Namespace(full_catalog=False, program=["BCS", "Data Science"])

    assert build_metadata(full, retain_raw=True) == {
        "scope": "full_catalog",
        "program_selectors": [],
        "raw_snapshot": True,
    }
    assert build_metadata(slice_args, retain_raw=False) == {
        "scope": "program_slice",
        "program_selectors": ["BCS", "Data Science"],
        "raw_snapshot": False,
    }


def test_backfill_resume_verifies_and_skips_existing_release(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    year = "2026-2027"
    (tmp_path / year).mkdir()
    args = argparse.Namespace(
        academic_years=[year],
        all_available=False,
        output=tmp_path,
        resume=True,
        force=False,
        without_raw=False,
        full_catalog=True,
        program=None,
        workers=8,
        max_courses=5000,
    )
    verified = {
        "valid": True,
        "academic_year": year,
        "course_count": 10,
        "program_count": 2,
        "publishable": True,
        "planner_ready": False,
        "build": {
            "scope": "full_catalog",
            "program_selectors": [],
            "raw_snapshot": True,
        },
    }
    monkeypatch.setattr(cli, "verify_catalog_directory", lambda _target: verified)
    monkeypatch.setattr(
        cli,
        "build_release",
        lambda *_args, **_kwargs: pytest.fail("existing release should be skipped"),
    )

    assert run_backfill(FakeAdapter([year]), args) == [{"status": "skipped", **verified}]


def test_backfill_resume_rejects_a_different_build_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    year = "2026-2027"
    (tmp_path / year).mkdir()
    args = argparse.Namespace(
        academic_years=[year],
        all_available=False,
        output=tmp_path,
        resume=True,
        force=False,
        without_raw=False,
        full_catalog=True,
        program=None,
        workers=8,
        max_courses=5000,
    )
    monkeypatch.setattr(
        cli,
        "verify_catalog_directory",
        lambda _target: {
            "publishable": True,
            "build": {
                "scope": "program_slice",
                "program_selectors": ["BCS"],
                "raw_snapshot": True,
            },
        },
    )

    with pytest.raises(VerificationError, match="does not match"):
        run_backfill(FakeAdapter([year]), args)


def test_backfill_resume_rejects_an_unpublishable_release(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    year = "2026-2027"
    (tmp_path / year).mkdir()
    args = argparse.Namespace(
        academic_years=[year],
        all_available=False,
        output=tmp_path,
        resume=True,
        force=False,
        without_raw=False,
        full_catalog=True,
        program=None,
        workers=8,
        max_courses=5000,
    )
    monkeypatch.setattr(
        cli,
        "verify_catalog_directory",
        lambda _target: {"publishable": False},
    )

    with pytest.raises(VerificationError, match="is not publishable"):
        run_backfill(FakeAdapter([year]), args)


def test_unpublishable_release_is_not_swapped_into_place(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    year = "2026-2027"
    args = argparse.Namespace(
        output=tmp_path,
        force=False,
        full_catalog=True,
        program=None,
        workers=1,
        max_courses=5000,
    )
    monkeypatch.setattr(
        cli,
        "publish_catalog",
        lambda _catalog, staging, **_kwargs: (
            (staging / year).mkdir(),
            {"generated_at": "now", "source_id": "source"},
        )[1],
    )
    monkeypatch.setattr(
        cli,
        "verify_catalog_directory",
        lambda _target: {"publishable": False},
    )
    monkeypatch.setattr(
        cli,
        "replace_snapshot",
        lambda *_args: pytest.fail("unpublishable release must not be swapped"),
    )

    with pytest.raises(VerificationError, match="publishable release gate"):
        build_release(FakeAdapter([year]), args, year, retain_raw=False)

    assert not (tmp_path / year).exists()
