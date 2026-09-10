import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from uwpath_data.artifacts import RawSnapshotWriter, publish_catalog
from uwpath_data.http import JsonHttpClient
from uwpath_data.sources.kuali import KUALI_API, KualiAdapter, KualiSnapshotAdapter


def _course(
    record_id: str,
    code: str,
    *,
    prerequisites: str = "",
    antirequisites: str = "",
) -> dict:
    return {
        "id": record_id,
        "pid": f"course-{code.lower()}",
        "__catalogCourseId": code,
        "subjectCode": {"name": "".join(character for character in code if character.isalpha())},
        "title": f"Title for {code}",
        "description": f"Description for {code}",
        "credits": {"value": "0.50"},
        "prerequisites": prerequisites,
        "corequisites": "",
        "antirequisites": antirequisites,
    }


def _responses() -> dict[str, object]:
    year = "2026-2027"
    title = f"{year} Undergraduate Studies Academic Calendar"
    cs_record = "aaaaaaaaaaaaaaaaaaaaaaaa"
    math_record = "bbbbbbbbbbbbbbbbbbbbbbbb"
    unrelated_record = "cccccccccccccccccccccccc"
    program_requirements = """
      <li data-test="ruleView-completionRequirement">
        Complete all of the following:
        <a href="#/courses/view/aaaaaaaaaaaaaaaaaaaaaaaa">CS 135</a>
      </li>
    """
    prerequisite = """
      <li data-test="ruleView-courseRequirement">
        <a href="#/courses/view/bbbbbbbbbbbbbbbbbbbbbbbb">MATH 135</a>
      </li>
    """
    return {
        f"{KUALI_API}/public/catalogs": [
            {
                "_id": "catalog-2026",
                "title": title,
                "startDate": "2026-09-01",
                "endDate": "2027-08-31",
            }
        ],
        f"{KUALI_API}/public/catalogs/catalog-2026": {
            "_id": "catalog-2026",
            "title": title,
            "startDate": "2026-09-01",
            "endDate": "2027-08-31",
        },
        f"{KUALI_API}/courses/catalog-2026": [
            {"id": "aaaaaaaaaaaaaaaaaaaaaaaa", "__catalogCourseId": "CS135"},
            {"id": "bbbbbbbbbbbbbbbbbbbbbbbb", "__catalogCourseId": "MATH135"},
            {"id": unrelated_record, "__catalogCourseId": "HIST101"},
        ],
        f"{KUALI_API}/programs/catalog-2026": [
            {"pid": "bcs", "code": "BCS", "title": "Computer Science (BCS)"},
            {"pid": "history", "code": "HIST", "title": "History"},
        ],
        f"{KUALI_API}/program/catalog-2026/bcs": {
            "id": "bcs-record",
            "pid": "bcs",
            "code": "BCS",
            "title": "Computer Science (BCS)",
            "undergraduateCredentialType": {"name": "Bachelor's Degree"},
            "fieldOfStudy": {"name": "Computer Science"},
            "facultyCalendarDisplay": {"name": "Mathematics"},
            "courseRequirementsNoUnits": program_requirements,
        },
        f"{KUALI_API}/program/catalog-2026/history": {
            "id": "history-record",
            "pid": "history",
            "code": "HIST",
            "title": "History",
            "courseRequirementsNoUnits": "",
        },
        f"{KUALI_API}/course/byId/catalog-2026/{cs_record}": _course(
            cs_record,
            "CS135",
            prerequisites=prerequisite,
            antirequisites="<p>Not completed any of the following: CS999</p>",
        ),
        f"{KUALI_API}/course/byId/catalog-2026/{math_record}": _course(math_record, "MATH135"),
        f"{KUALI_API}/course/byId/catalog-2026/{unrelated_record}": _course(
            unrelated_record, "HIST101"
        ),
    }


def test_build_program_slice_follows_course_dependencies_and_publishes(tmp_path: Path) -> None:
    responses = _responses()
    requested_urls: list[str] = []

    def transport(url: str):
        requested_urls.append(url)
        return responses[url]

    adapter = KualiAdapter(JsonHttpClient(KUALI_API, transport=transport))
    raw_writer = RawSnapshotWriter(tmp_path / "raw")

    catalog = adapter.build_catalog(
        "2026-2027",
        ["BCS"],
        workers=2,
        raw_sink=raw_writer,
    )
    manifest = publish_catalog(catalog, tmp_path / "published")

    assert [course.course_code for course in catalog.courses] == ["CS 135", "MATH 135"]
    assert catalog.quality.dangling_course_references == ()
    assert catalog.quality.external_course_references == ("CS 999",)
    assert catalog.quality.publishable
    assert catalog.quality.planner_ready
    assert (
        requested_urls.count(f"{KUALI_API}/course/byId/catalog-2026/bbbbbbbbbbbbbbbbbbbbbbbb") == 1
    )
    assert (tmp_path / "raw/courses/aaaaaaaaaaaaaaaaaaaaaaaa.json").exists()
    assert (tmp_path / "raw/catalog-index.json").exists()
    assert manifest["files"]["catalog.json"]["sha256"]

    catalog_path = tmp_path / "published/2026-2027/catalog.json"
    schema_path = Path(__file__).parents[1] / "schema/catalog-v1.schema.json"
    instance = json.loads(catalog_path.read_text())
    schema = json.loads(schema_path.read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(instance)

    replayed = KualiSnapshotAdapter(tmp_path / "raw").build_catalog("2026-2027", ["BCS"], workers=1)
    replayed_data = replayed.to_dict()
    original_data = catalog.to_dict()
    replayed_data.pop("generated_at")
    original_data.pop("generated_at")
    assert replayed_data == original_data


def test_archived_catalog_replay_preserves_source_urls(tmp_path: Path) -> None:
    responses = _responses()
    responses[f"{KUALI_API}/public/catalogs"].append(
        {
            "_id": "catalog-2027",
            "title": "2027-2028 Undergraduate Studies Academic Calendar",
            "startDate": "2027-09-01",
            "endDate": "2028-08-31",
        }
    )
    adapter = KualiAdapter(JsonHttpClient(KUALI_API, transport=responses.__getitem__))
    raw_writer = RawSnapshotWriter(tmp_path / "raw")

    catalog = adapter.build_catalog(
        "2026-2027",
        ["BCS"],
        workers=1,
        raw_sink=raw_writer,
    )
    replayed = KualiSnapshotAdapter(tmp_path / "raw").build_catalog(
        "2026-2027", ["BCS"], workers=1
    )

    assert "/archive/2026-2027" in catalog.calendar.source_url
    replayed_data = replayed.to_dict()
    original_data = catalog.to_dict()
    replayed_data.pop("generated_at")
    original_data.pop("generated_at")
    assert replayed_data == original_data


def test_full_catalog_fetches_all_programs_and_active_courses() -> None:
    responses = _responses()
    adapter = KualiAdapter(JsonHttpClient(KUALI_API, transport=responses.__getitem__))
    progress: list[str] = []

    catalog = adapter.build_catalog("2026-2027", None, workers=2, progress=progress.append)

    assert [course.course_code for course in catalog.courses] == [
        "CS 135",
        "HIST 101",
        "MATH 135",
    ]
    assert [program.code for program in catalog.programs] == ["BCS", "HIST"]
    assert catalog.quality.dangling_course_references == ()
    assert progress == [
        "selected 2 programs from 3 active courses",
        "fetched 2/2 program details",
        "fetched 3/3 course details",
    ]


def test_program_order_is_stable_when_titles_match() -> None:
    responses = _responses()
    program_index_url = f"{KUALI_API}/programs/catalog-2026"
    program_bcs_url = f"{KUALI_API}/program/catalog-2026/bcs"
    program_history_url = f"{KUALI_API}/program/catalog-2026/history"
    responses[program_index_url] = list(reversed(responses[program_index_url]))
    responses[program_bcs_url]["title"] = "Shared title"
    responses[program_history_url]["title"] = "Shared title"
    adapter = KualiAdapter(JsonHttpClient(KUALI_API, transport=responses.__getitem__))

    catalog = adapter.build_catalog("2026-2027", None, workers=1)

    assert [program.code for program in catalog.programs] == ["BCS", "HIST"]


def test_program_selector_rejects_ambiguous_matches() -> None:
    adapter = KualiAdapter(JsonHttpClient(KUALI_API, transport=lambda _url: []))
    programs = [
        {"pid": "one", "title": "Computer Science"},
        {"pid": "two", "title": "Computer Science Minor"},
    ]

    try:
        adapter.select_programs(programs, ["Computer"])
    except ValueError as error:
        assert "matched 2 programs" in str(error)
    else:
        raise AssertionError("Expected an ambiguous selector to be rejected")


def test_raw_snapshot_writer_rejects_path_traversal(tmp_path: Path) -> None:
    writer = RawSnapshotWriter(tmp_path / "raw")

    try:
        writer("../outside.json", {})
    except ValueError as error:
        assert "escapes its root" in str(error)
    else:
        raise AssertionError("Expected path traversal to be rejected")

    assert not (tmp_path / "outside.json").exists()
