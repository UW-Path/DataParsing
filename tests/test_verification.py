from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from uwpath_data.artifacts import publish_catalog
from uwpath_data.comparison import compare_catalogs
from uwpath_data.models import Calendar, Catalog, Course, Program, QualityReport
from uwpath_data.verification import VerificationError, verify_catalog_directory


def _catalog(year: str, course_codes: tuple[str, ...]) -> Catalog:
    courses = tuple(
        Course(
            id=f"id-{code}",
            source_record_id=f"record-{code}",
            course_code=code,
            source_course_code=code.replace(" ", ""),
            subject=code.split()[0],
            number=code.split()[1],
            title=f"Title for {code}",
            description="",
            units="0.50",
            prerequisites_html="",
            corequisites_html="",
            antirequisites_html="",
            prerequisite_rule=None,
            corequisite_rule=None,
            antirequisite_rule=None,
            source_url=f"https://example.com/{year}/{code.replace(' ', '')}",
            source_hash=(str(index + 1) * 64)[:64],
        )
        for index, code in enumerate(course_codes)
    )
    program = Program(
        id="bcs",
        source_record_id="bcs-record",
        code="BCS",
        title="Computer Science",
        credential_type="Major",
        field_of_study="Computer Science",
        faculty="Mathematics",
        requirements_html="",
        requirement_rule=None,
        source_url=f"https://example.com/{year}/bcs",
        source_hash="a" * 64,
    )
    return Catalog(
        generated_at=datetime.now(timezone.utc).isoformat(),
        calendar=Calendar(
            academic_year=year,
            title=f"{year} Undergraduate Calendar",
            source="fixture",
            source_id=f"catalog-{year}",
            source_url=f"https://example.com/{year}",
            starts_on=f"{year[:4]}-09-01",
            ends_on=f"{year[-4:]}-08-31",
        ),
        courses=courses,
        programs=(program,),
        quality=QualityReport(
            course_count=len(courses),
            program_count=1,
            rule_count=0,
            manual_rule_count=0,
        ),
    )


def test_verify_catalog_checks_schema_projections_counts_and_hashes(tmp_path: Path) -> None:
    catalog = _catalog("2026-2027", ("CS 135", "MATH 135"))
    publish_catalog(catalog, tmp_path)
    root = tmp_path / "2026-2027"

    assert verify_catalog_directory(root) == {
        "valid": True,
        "academic_year": "2026-2027",
        "course_count": 2,
        "program_count": 1,
        "publishable": True,
        "planner_ready": True,
    }

    courses_path = root / "courses.json"
    courses_path.write_text(courses_path.read_text() + "\n")
    with pytest.raises(VerificationError, match="manifest byte count does not match"):
        verify_catalog_directory(root)


def test_compare_catalogs_fails_on_large_count_drop(tmp_path: Path) -> None:
    publish_catalog(_catalog("2025-2026", ("CS 135", "MATH 135")), tmp_path / "baseline")
    publish_catalog(_catalog("2026-2027", ("CS 135",)), tmp_path / "candidate")

    report = compare_catalogs(
        tmp_path / "baseline/2025-2026",
        tmp_path / "candidate/2026-2027",
    )

    assert report["courses"]["removed"] == ["MATH 135"]
    assert report["courses"]["count_delta_percent"] == -50.0
    assert not report["gates"]["passed"]
    assert report["gates"]["failures"] == ["course count dropped 50.00%, above 10.00%"]
