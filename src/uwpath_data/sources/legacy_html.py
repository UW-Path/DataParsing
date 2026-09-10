from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag

from uwpath_data.http import HttpNotFound, TextHttpClient
from uwpath_data.models import Calendar, Catalog, Course, QualityReport, Rule
from uwpath_data.rules import (
    extract_course_codes,
    format_course_code,
    normalize_text,
    referenced_course_codes,
    walk_rules,
)

LEGACY_ROOT = "https://ucalendar.uwaterloo.ca"
LEGACY_YEAR_CODES = {
    "2019-2020": "1920",
    "2020-2021": "2021",
    "2021-2022": "2122",
    "2022-2023": "2223",
}
LEGACY_SUBJECTS = (
    "ACTSC",
    "AE",
    "AFM",
    "AHS",
    "AMATH",
    "ANTH",
    "APPLS",
    "ARABIC",
    "ARBUS",
    "ARCH",
    "ARTS",
    "ASL",
    "AVIA",
    "BASE",
    "BET",
    "BIOL",
    "BLKST",
    "BME",
    "BUS",
    "CDNST",
    "CFM",
    "CHE",
    "CHEM",
    "CHINA",
    "CI",
    "CIVE",
    "CLAS",
    "CMW",
    "CO",
    "COGSCI",
    "COMM",
    "COMMST",
    "COOP",
    "CROAT",
    "CS",
    "DAC",
    "DUTCH",
    "EARTH",
    "EASIA",
    "ECE",
    "ECON",
    "EMLS",
    "ENBUS",
    "ENGL",
    "ENVE",
    "ENVS",
    "ERS",
    "FINE",
    "FR",
    "GBDA",
    "GENE",
    "GEOE",
    "GEOG",
    "GER",
    "GERON",
    "GRK",
    "GSJ",
    "HEALTH",
    "HIST",
    "HHUM",
    "HLTH",
    "HRM",
    "HRTS",
    "HUMSC",
    "INDEV",
    "INDENT",
    "INDG",
    "INTEG",
    "INTST",
    "ITAL",
    "ITALST",
    "JAPAN",
    "JS",
    "KIN",
    "KOREA",
    "LAT",
    "LS",
    "MATBUS",
    "MATH",
    "ME",
    "MEDVL",
    "MENN",
    "MGMT",
    "MNS",
    "MOHAWK",
    "MSCI",
    "MTE",
    "MTHEL",
    "MUSIC",
    "NE",
    "OPTOM",
    "PACS",
    "PD",
    "PDARCH",
    "PDPHRM",
    "PHARM",
    "PHIL",
    "PHYS",
    "PLAN",
    "PMATH",
    "PORT",
    "PSCI",
    "PSYCH",
    "REC",
    "REES",
    "RS",
    "RUSS",
    "SCBUS",
    "SCI",
    "SDS",
    "SE",
    "SFM",
    "SI",
    "SMF",
    "SOC",
    "SOCWK",
    "SPAN",
    "SPCOM",
    "STAT",
    "STV",
    "SVENT",
    "SWREN",
    "SYDE",
    "THPERF",
    "UNIV",
    "VCULT",
    "WKRPT",
)

SUBJECT_RE = re.compile(r"^[A-Z]{2,8}$")
COURSE_ANCHOR_RE = re.compile(r"^(?P<subject>[A-Z]{2,8})(?P<number>\d{1,4}[A-Z]?)$")
COURSE_ID_RE = re.compile(r"Course ID:\s*(\S+)", re.IGNORECASE)
UNIT_RE = re.compile(r"(?P<units>\d+(?:\.\d+)?)\s*$")
REQUIREMENT_RE = re.compile(r"^(Prereq|Coreq|Antireq):\s*(.*)$", re.IGNORECASE)
SHORTHAND_RE = re.compile(
    r"\b(?P<subject>[A-Z]{2,8})\s*(?P<number>\d{1,4}[A-Z]?)"
    r"(?P<tail>(?:\s*(?:,|/|(?i:\bor\b)|(?i:\band\b))\s*\d{2,4}[A-Z]?)+)"
)
SHORTHAND_NUMBER_RE = re.compile(r"\d{2,4}[A-Z]?")
NON_COURSE_SUBJECTS = frozenset(
    {
        "CLN",
        "DIS",
        "ENS",
        "ESS",
        "FLD",
        "FLT",
        "LAB",
        "LEC",
        "OLN",
        "ORL",
        "PRA",
        "PRJ",
        "RDG",
        "SEM",
        "STU",
        "TLC",
        "TST",
        "TUT",
        "WRK",
        "WSP",
    }
)

RawTextSink = Callable[[str, str], None]
Progress = Callable[[str], None]


@dataclass(frozen=True)
class LegacyBuildResult:
    catalog: Catalog
    requested_subjects: tuple[str, ...]
    fetched_subjects: tuple[str, ...]
    missing_subjects: tuple[str, ...]
    empty_subjects: tuple[str, ...]


def _legacy_year_code(academic_year: str) -> str:
    try:
        return LEGACY_YEAR_CODES[academic_year]
    except KeyError as error:
        available = ", ".join(LEGACY_YEAR_CODES)
        raise ValueError(
            f"No static legacy course catalog for {academic_year}. Available: {available}"
        ) from error


def _subject(value: str) -> str:
    normalized = value.strip().upper()
    if not SUBJECT_RE.fullmatch(normalized):
        raise ValueError(f"Invalid legacy course subject: {value!r}")
    return normalized


def _source_url(academic_year: str, subject: str) -> str:
    year_code = _legacy_year_code(academic_year)
    return f"{LEGACY_ROOT}/{year_code}/COURSE/course-{subject}.html"


def _source_hash(source_fragment: str) -> str:
    normalized = source_fragment.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode()).hexdigest()


def _requirement_fragments(course_element: Tag) -> dict[str, str]:
    fragments: dict[str, list[str]] = {
        "prerequisite": [],
        "corequisite": [],
        "antirequisite": [],
    }
    labels = {
        "prereq": "prerequisite",
        "coreq": "corequisite",
        "antireq": "antirequisite",
    }
    for element in course_element.find_all(["em", "i"]):
        text = normalize_text(element.get_text(" ", strip=True))
        match = REQUIREMENT_RE.match(text)
        if not match:
            continue
        field_name = labels[match.group(1).lower()]
        body = match.group(2).strip()
        if body:
            fragments[field_name].append(body)
    return {field_name: "<br>".join(values) for field_name, values in fragments.items()}


def _legacy_course_codes(value: str) -> tuple[str, ...]:
    codes = [
        code
        for code in extract_course_codes(value)
        if code.split(" ", 1)[0] not in NON_COURSE_SUBJECTS
    ]
    text = BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)
    for match in SHORTHAND_RE.finditer(text):
        subject = match.group("subject")
        if subject in NON_COURSE_SUBJECTS:
            continue
        codes.append(format_course_code(f"{subject}{match.group('number')}"))
        codes.extend(
            format_course_code(f"{subject}{number}")
            for number in SHORTHAND_NUMBER_RE.findall(match.group("tail"))
        )
    return tuple(dict.fromkeys(codes))


def parse_legacy_rule(value: str, kind: str) -> Rule | None:
    text = normalize_text(BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True))
    if not text:
        return None
    codes = _legacy_course_codes(text)
    children = tuple(Rule(type="course", source_text=code, course_code=code) for code in codes)
    if kind == "antirequisite" and children:
        return Rule(type="none_of", source_text=text, children=children)
    if len(children) == 1 and text.casefold() == children[0].course_code.casefold():
        return children[0]
    return Rule(
        type="manual",
        source_text=text,
        children=children,
        reason="legacy_unstructured_text",
    )


def parse_legacy_subject_page(
    academic_year: str,
    subject: str,
    html: str,
) -> tuple[Course, ...]:
    normalized_subject = _subject(subject)
    soup = BeautifulSoup(html, "html.parser")
    courses: list[Course] = []
    for course_element in soup.find_all("center"):
        anchor = course_element.find("a", attrs={"name": True})
        anchor_name = str(anchor.get("name", "")).strip().upper() if anchor else ""
        match = COURSE_ANCHOR_RE.fullmatch(anchor_name)
        if not match or match.group("subject") != normalized_subject:
            continue

        cells = course_element.select(".divTableCell")
        if len(cells) < 4:
            cells = course_element.find_all("td")
        if len(cells) < 4:
            raise ValueError(f"Unsupported legacy markup for {anchor_name}")
        course_code = format_course_code(anchor_name)
        header = normalize_text(cells[0].get_text(" ", strip=True))
        id_match = COURSE_ID_RE.search(cells[1].get_text(" ", strip=True))
        source_record_id = id_match.group(1) if id_match else anchor_name
        unit_match = UNIT_RE.search(header)
        requirements = _requirement_fragments(course_element)
        source_fragment = str(course_element)
        courses.append(
            Course(
                id=source_record_id,
                source_record_id=source_record_id,
                course_code=course_code,
                source_course_code=anchor_name,
                subject=normalized_subject,
                number=match.group("number"),
                title=normalize_text(cells[2].get_text(" ", strip=True)),
                description=normalize_text(cells[3].get_text(" ", strip=True)),
                units=unit_match.group("units") if unit_match else None,
                prerequisites_html=requirements["prerequisite"],
                corequisites_html=requirements["corequisite"],
                antirequisites_html=requirements["antirequisite"],
                prerequisite_rule=parse_legacy_rule(requirements["prerequisite"], "prerequisite"),
                corequisite_rule=parse_legacy_rule(requirements["corequisite"], "corequisite"),
                antirequisite_rule=parse_legacy_rule(
                    requirements["antirequisite"], "antirequisite"
                ),
                source_url=f"{_source_url(academic_year, normalized_subject)}#{anchor_name}",
                source_hash=_source_hash(source_fragment),
            )
        )
    return tuple(sorted(courses, key=lambda course: course.course_code))


def _quality(courses: tuple[Course, ...]) -> QualityReport:
    course_codes = [course.course_code for course in courses]
    duplicate_codes = tuple(
        sorted(code for code in set(course_codes) if course_codes.count(code) > 1)
    )
    all_rules = [
        rule
        for course in courses
        for root in (
            course.prerequisite_rule,
            course.corequisite_rule,
            course.antirequisite_rule,
        )
        for rule in walk_rules(root)
    ]
    referenced_codes = {
        code
        for course in courses
        for rule in (
            course.prerequisite_rule,
            course.corequisite_rule,
            course.antirequisite_rule,
        )
        for code in referenced_course_codes(rule)
    }
    available_codes = set(course_codes)
    external = tuple(sorted(referenced_codes - available_codes))
    warnings: list[str] = []
    if any(rule.type == "manual" for rule in all_rules):
        warnings.append(
            "Some legacy rules require manual interpretation; inspect manual_rule_count before use."
        )
    if external:
        warnings.append(
            "Some rules reference courses outside this legacy snapshot; "
            "inspect external_course_references before use."
        )
    return QualityReport(
        course_count=len(courses),
        program_count=0,
        rule_count=len(all_rules),
        manual_rule_count=sum(rule.type == "manual" for rule in all_rules),
        duplicate_course_codes=duplicate_codes,
        external_course_references=external,
        warnings=tuple(warnings),
    )


class LegacyHtmlAdapter:
    def __init__(self, client: TextHttpClient | None = None) -> None:
        self.client = client or TextHttpClient(LEGACY_ROOT)

    def fetch_subject(self, academic_year: str, subject: str) -> str:
        year_code = _legacy_year_code(academic_year)
        return self.client.get(f"{year_code}/COURSE/course-{subject}.html")

    def build_catalog(
        self,
        academic_year: str,
        subjects: Iterable[str] | None,
        *,
        workers: int = 8,
        max_courses: int = 5000,
        raw_sink: RawTextSink | None = None,
        progress: Progress | None = None,
    ) -> LegacyBuildResult:
        year_code = _legacy_year_code(academic_year)
        full_catalog = subjects is None
        requested = tuple(
            LEGACY_SUBJECTS
            if full_catalog
            else sorted({_subject(value) for value in subjects or ()})
        )
        if not requested:
            raise ValueError("Select at least one legacy course subject")

        pages: dict[str, str] = {}
        missing: list[str] = []
        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            futures = {
                executor.submit(self.fetch_subject, academic_year, subject): subject
                for subject in requested
            }
            total = len(futures)
            for completed, future in enumerate(as_completed(futures), start=1):
                subject = futures[future]
                try:
                    pages[subject] = future.result()
                except HttpNotFound:
                    if not full_catalog:
                        raise ValueError(
                            f"Legacy subject {subject} is not available for {academic_year}"
                        ) from None
                    missing.append(subject)
                if progress and (completed % 10 == 0 or completed == total):
                    progress(f"fetched {completed}/{total} legacy subject pages")

        parsed_pages = {
            subject: parse_legacy_subject_page(academic_year, subject, html)
            for subject, html in pages.items()
        }
        empty = tuple(sorted(subject for subject, courses in parsed_pages.items() if not courses))
        if raw_sink:
            for subject, html in sorted(pages.items()):
                raw_sink(f"subjects/{subject}.html", html)
            raw_sink(
                "snapshot.json",
                json.dumps(
                    {
                        "academic_year": academic_year,
                        "scope": "full_catalog" if full_catalog else "subject_slice",
                        "requested_subjects": requested,
                        "fetched_subjects": sorted(pages),
                        "missing_subjects": sorted(missing),
                        "empty_subjects": empty,
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
            )
        if empty and not full_catalog:
            raise ValueError(
                "Legacy subject pages did not contain concrete courses: " + ", ".join(empty)
            )
        courses = tuple(
            sorted(
                (course for subject_courses in parsed_pages.values() for course in subject_courses),
                key=lambda course: course.course_code,
            )
        )
        if len(courses) > max_courses:
            raise ValueError(
                f"Legacy catalog contains {len(courses)} courses, exceeding "
                f"max_courses={max_courses}"
            )
        start_year = int(academic_year[:4])
        calendar = Calendar(
            academic_year=academic_year,
            title=f"{academic_year} Undergraduate Studies Calendar",
            source="uwaterloo_legacy_html",
            source_id=year_code,
            source_url=f"{LEGACY_ROOT}/{year_code}/",
            starts_on=date(start_year, 9, 1).isoformat(),
            ends_on=date(start_year + 1, 8, 31).isoformat(),
        )
        catalog = Catalog(
            generated_at=datetime.now(timezone.utc).isoformat(),
            calendar=calendar,
            courses=courses,
            programs=(),
            quality=_quality(courses),
        )
        return LegacyBuildResult(
            catalog=catalog,
            requested_subjects=requested,
            fetched_subjects=tuple(sorted(pages)),
            missing_subjects=tuple(sorted(missing)),
            empty_subjects=empty,
        )


class LegacyHtmlSnapshotAdapter(LegacyHtmlAdapter):
    def __init__(self, snapshot_root: Path) -> None:
        self.snapshot_root = snapshot_root.resolve()
        metadata_path = self.snapshot_root / "snapshot.json"
        try:
            metadata: Any = json.loads(metadata_path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Could not read legacy snapshot metadata: {error}") from error
        if not isinstance(metadata, dict):
            raise ValueError("Legacy snapshot metadata must be an object")
        self.metadata = metadata
        super().__init__(TextHttpClient(LEGACY_ROOT, transport=self._read_url))

    def _read_url(self, url: str) -> str:
        match = re.search(r"/course-([A-Z]{2,8})\.html$", url)
        if not match:
            raise ValueError(f"Unsupported legacy snapshot URL: {url}")
        path = (self.snapshot_root / "subjects" / f"{match.group(1)}.html").resolve()
        if not path.is_relative_to(self.snapshot_root):
            raise ValueError("Legacy snapshot path escapes its root")
        try:
            return path.read_text()
        except FileNotFoundError as error:
            raise ValueError(f"Legacy snapshot is missing {path.name}") from error

    def build_catalog(
        self,
        academic_year: str,
        subjects: Iterable[str] | None,
        **kwargs: Any,
    ) -> LegacyBuildResult:
        if self.metadata.get("academic_year") != academic_year:
            raise ValueError("Legacy snapshot academic year does not match the requested year")
        fetched = self.metadata.get("fetched_subjects")
        if not isinstance(fetched, list) or not all(isinstance(value, str) for value in fetched):
            raise ValueError("Legacy snapshot fetched_subjects are invalid")
        snapshot_scope = self.metadata.get("scope")
        if snapshot_scope not in {"full_catalog", "subject_slice"}:
            raise ValueError("Legacy snapshot scope is invalid")
        if subjects is None and snapshot_scope != "full_catalog":
            raise ValueError("A subject-slice snapshot cannot be rebuilt as a full catalog")
        recorded_empty = self.metadata.get("empty_subjects", [])
        if not isinstance(recorded_empty, list) or not all(
            isinstance(value, str) for value in recorded_empty
        ):
            raise ValueError("Legacy snapshot empty_subjects are invalid")
        selected = (
            [subject for subject in fetched if subject not in recorded_empty]
            if subjects is None
            else subjects
        )
        result = super().build_catalog(academic_year, selected, **kwargs)
        if subjects is not None:
            return result
        requested = self.metadata.get("requested_subjects")
        missing = self.metadata.get("missing_subjects")
        empty = recorded_empty
        if not isinstance(requested, list) or not all(
            isinstance(value, str) for value in requested
        ):
            raise ValueError("Legacy snapshot requested_subjects are invalid")
        if not isinstance(missing, list) or not all(isinstance(value, str) for value in missing):
            raise ValueError("Legacy snapshot missing_subjects are invalid")
        if not isinstance(empty, list) or not all(isinstance(value, str) for value in empty):
            raise ValueError("Legacy snapshot empty_subjects are invalid")
        return LegacyBuildResult(
            catalog=result.catalog,
            requested_subjects=tuple(requested),
            fetched_subjects=tuple(fetched),
            missing_subjects=tuple(missing),
            empty_subjects=tuple(empty),
        )
