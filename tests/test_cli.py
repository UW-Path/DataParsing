import argparse
from pathlib import Path

import pytest

from uwpath_data.cli import academic_year, prepare_target, replace_snapshot


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
