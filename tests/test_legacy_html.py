from pathlib import Path

import pytest

from uwpath_data.artifacts import RawTextSnapshotWriter
from uwpath_data.http import HttpNotFound, TextHttpClient
from uwpath_data.rules import referenced_course_codes
from uwpath_data.sources import legacy_html
from uwpath_data.sources.legacy_html import (
    LEGACY_ROOT,
    LegacyHtmlAdapter,
    LegacyHtmlSnapshotAdapter,
    parse_legacy_rule,
    parse_legacy_subject_page,
)


def _subject_page() -> str:
    return """
    <html><body>
      <center>
        <div class="divTable">
          <div class="divTableCell"><strong><a name="CS100"></a>CS 100 LEC 0.50</strong></div>
          <div class="divTableCell crseid">Course ID: 004360</div>
          <div class="divTableCell colspan-2"><strong>Introduction to Computing</strong></div>
          <div class="divTableCell colspan-2">A useful description. [Offered: F,W,S]</div>
          <div class="divTableCell colspan-2"><em>Prereq: CS 105; instructor consent</em></div>
          <div class="divTableCell colspan-2"><em>Antireq: CS 115, 135, 137, CHE 121</em></div>
        </div>
      </center>
      <center>
        <div class="divTable">
          <div class="divTableCell"><strong><a name="CS105"></a>CS 105 LAB,LEC 0.50</strong></div>
          <div class="divTableCell crseid">Course ID: 015054</div>
          <div class="divTableCell colspan-2"><strong>Programming 1</strong></div>
          <div class="divTableCell colspan-2">Another description.</div>
          <div class="divTableCell colspan-2"><em>Prereq: </em></div>
        </div>
      </center>
    </body></html>
    """


def _table_subject_page() -> str:
    return """
    <center><table>
      <tr>
        <td><b><a name="ACTSC221"></a>ACTSC 221 LEC 0.50</b></td>
        <td>Course ID: 003290</td>
      </tr>
      <tr><td colspan="2"><b>Introductory Financial Mathematics</b></td></tr>
      <tr><td colspan="2">Rates of interest and discount.</td></tr>
      <tr><td colspan="2"><i>Prereq: Level at least 2A.</i></td></tr>
      <tr><td colspan="2"><i>Antireq: ACTSC 231</i></td></tr>
    </table></center>
    """


def test_parses_legacy_course_fields_and_preserves_complex_rules() -> None:
    courses = parse_legacy_subject_page("2022-2023", "CS", _subject_page())

    assert [course.course_code for course in courses] == ["CS 100", "CS 105"]
    course = courses[0]
    assert course.id == "004360"
    assert course.number == "100"
    assert course.units == "0.50"
    assert course.title == "Introduction to Computing"
    assert course.prerequisite_rule.type == "manual"
    assert course.prerequisite_rule.reason == "legacy_unstructured_text"
    assert course.antirequisite_rule.type == "none_of"
    assert referenced_course_codes(course.antirequisite_rule) == {
        "CHE 121",
        "CS 115",
        "CS 135",
        "CS 137",
    }
    crlf_courses = parse_legacy_subject_page(
        "2022-2023", "CS", _subject_page().replace("\n", "\r\n")
    )
    assert [item.source_hash for item in crlf_courses] == [item.source_hash for item in courses]


def test_parses_older_table_based_course_markup() -> None:
    courses = parse_legacy_subject_page("2019-2020", "ACTSC", _table_subject_page())

    assert len(courses) == 1
    assert courses[0].course_code == "ACTSC 221"
    assert courses[0].title == "Introductory Financial Mathematics"
    assert courses[0].description == "Rates of interest and discount."
    assert referenced_course_codes(courses[0].antirequisite_rule) == {"ACTSC 231"}


def test_network_snapshot_replays_without_network_requests(tmp_path: Path) -> None:
    page_url = f"{LEGACY_ROOT}/2223/COURSE/course-CS.html"
    client = TextHttpClient(LEGACY_ROOT, transport={page_url: _subject_page()}.__getitem__)
    raw_root = tmp_path / "raw"
    network = LegacyHtmlAdapter(client).build_catalog(
        "2022-2023",
        ["cs"],
        workers=1,
        raw_sink=RawTextSnapshotWriter(raw_root),
    )

    replay = LegacyHtmlSnapshotAdapter(raw_root).build_catalog(
        "2022-2023",
        ["CS"],
        workers=1,
    )

    network_data = network.catalog.to_dict()
    replay_data = replay.catalog.to_dict()
    network_data.pop("generated_at")
    replay_data.pop("generated_at")
    assert replay_data == network_data
    assert network.fetched_subjects == ("CS",)
    assert network.missing_subjects == ()
    assert network.empty_subjects == ()
    assert (raw_root / "subjects/CS.html").read_text() == _subject_page()

    with pytest.raises(ValueError, match="cannot be rebuilt as a full catalog"):
        LegacyHtmlSnapshotAdapter(raw_root).build_catalog(
            "2022-2023",
            None,
            workers=1,
        )


def test_full_snapshot_records_missing_and_empty_subject_pages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(legacy_html, "LEGACY_SUBJECTS", ("AHS", "BUS", "CS"))
    responses = {
        f"{LEGACY_ROOT}/2223/COURSE/course-BUS.html": "<center><a name='BUS-----'></a></center>",
        f"{LEGACY_ROOT}/2223/COURSE/course-CS.html": _subject_page(),
    }

    def transport(url: str) -> str:
        try:
            return responses[url]
        except KeyError as error:
            raise HttpNotFound(url) from error

    raw_root = tmp_path / "raw"
    network = LegacyHtmlAdapter(TextHttpClient(LEGACY_ROOT, transport=transport)).build_catalog(
        "2022-2023",
        None,
        workers=2,
        raw_sink=RawTextSnapshotWriter(raw_root),
    )
    replay = LegacyHtmlSnapshotAdapter(raw_root).build_catalog(
        "2022-2023",
        None,
        workers=1,
    )

    assert network.requested_subjects == ("AHS", "BUS", "CS")
    assert network.fetched_subjects == ("BUS", "CS")
    assert network.missing_subjects == ("AHS",)
    assert network.empty_subjects == ("BUS",)
    assert [course.course_code for course in replay.catalog.courses] == ["CS 100", "CS 105"]
    assert replay.fetched_subjects == network.fetched_subjects
    assert replay.missing_subjects == network.missing_subjects
    assert replay.empty_subjects == network.empty_subjects


def test_legacy_rule_ignores_course_components_and_unit_values() -> None:
    rule = parse_legacy_rule(
        "ARTS 290 (LEC 001) or FINE 327 and 1.0 unit of studio courses",
        "antirequisite",
    )

    assert referenced_course_codes(rule) == {"ARTS 290", "FINE 327"}


def test_raw_text_snapshot_writer_rejects_path_traversal(tmp_path: Path) -> None:
    writer = RawTextSnapshotWriter(tmp_path / "raw")

    try:
        writer("../outside.html", "content")
    except ValueError as error:
        assert "escapes its root" in str(error)
    else:
        raise AssertionError("Expected path traversal to be rejected")

    assert not (tmp_path / "outside.html").exists()
