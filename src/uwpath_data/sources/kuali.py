from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from uwpath_data.http import JsonHttpClient, JsonValue
from uwpath_data.models import Calendar, Catalog, Course, Program, QualityReport, Rule
from uwpath_data.rules import (
    extract_course_codes,
    extract_course_references,
    format_course_code,
    parse_kuali_rules,
    referenced_course_codes,
    walk_rules,
)

KUALI_ROOT = "https://uwaterloocm.kuali.co"
KUALI_API = f"{KUALI_ROOT}/api/v1/catalog"
UNDERGRADUATE_TITLE_RE = re.compile(
    r"^(?P<year>\d{4}-\d{4}) Undergraduate Studies Academic Calendar$"
)
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9._~-]+$")


def _object(value: JsonValue, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Expected object for {context}, got {type(value).__name__}")
    return value


def _objects(value: JsonValue, context: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError(f"Expected object array for {context}")
    return value


def _canonical_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _name(value: Any) -> str:
    return value.get("name", "") if isinstance(value, dict) else ""


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _identifier(value: Any, context: str) -> str:
    identifier = _text(value)
    if not IDENTIFIER_RE.fullmatch(identifier):
        raise ValueError(f"Invalid {context}: {identifier!r}")
    return identifier


class KualiAdapter:
    def __init__(self, client: JsonHttpClient | None = None) -> None:
        self.client = client or JsonHttpClient(KUALI_API)
        self._catalog_cache: list[dict[str, Any]] | None = None

    def list_undergraduate_catalogs(self) -> list[dict[str, Any]]:
        if self._catalog_cache is None:
            catalogs = _objects(self.client.get("public/catalogs"), "catalog list")
            self._catalog_cache = [
                catalog
                for catalog in catalogs
                if UNDERGRADUATE_TITLE_RE.match(catalog.get("title", ""))
            ]
        return list(self._catalog_cache)

    def resolve_catalog(self, academic_year: str) -> dict[str, Any]:
        for catalog in self.list_undergraduate_catalogs():
            match = UNDERGRADUATE_TITLE_RE.match(catalog.get("title", ""))
            if match and match.group("year") == academic_year:
                return catalog
        available = ", ".join(self.available_years())
        raise ValueError(
            f"No Kuali undergraduate catalog for {academic_year}. Available: {available}"
        )

    def available_years(self) -> list[str]:
        years = []
        for catalog in self.list_undergraduate_catalogs():
            match = UNDERGRADUATE_TITLE_RE.match(catalog.get("title", ""))
            if match:
                years.append(match.group("year"))
        return sorted(years)

    def fetch_catalog(self, catalog_id: str) -> dict[str, Any]:
        return _object(self.client.get(f"public/catalogs/{catalog_id}"), "catalog")

    def list_courses(self, catalog_id: str) -> list[dict[str, Any]]:
        return _objects(self.client.get(f"courses/{catalog_id}"), "course list")

    def list_programs(self, catalog_id: str) -> list[dict[str, Any]]:
        return _objects(self.client.get(f"programs/{catalog_id}"), "program list")

    def fetch_course(self, catalog_id: str, source_record_id: str) -> dict[str, Any]:
        return _object(
            self.client.get(f"course/byId/{catalog_id}/{source_record_id}"),
            f"course {source_record_id}",
        )

    def fetch_program(self, catalog_id: str, program_id: str) -> dict[str, Any]:
        return _object(
            self.client.get(f"program/{catalog_id}/{program_id}"),
            f"program {program_id}",
        )

    def select_programs(
        self, programs: list[dict[str, Any]], selectors: Iterable[str]
    ) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        for selector in selectors:
            normalized = selector.casefold()
            exact = [
                program
                for program in programs
                if normalized
                in {
                    str(program.get("pid", "")).casefold(),
                    str(program.get("code", "")).casefold(),
                    str(program.get("title", "")).casefold(),
                }
            ]
            matches = exact or [
                program
                for program in programs
                if normalized in str(program.get("title", "")).casefold()
            ]
            if len(matches) != 1:
                titles = ", ".join(str(program.get("title")) for program in matches[:5])
                raise ValueError(
                    f"Program selector {selector!r} matched {len(matches)} programs"
                    + (f": {titles}" if titles else "")
                )
            if matches[0] not in selected:
                selected.append(matches[0])
        return selected

    def build_catalog(
        self,
        academic_year: str,
        selectors: Iterable[str] | None,
        *,
        workers: int = 8,
        max_courses: int = 5000,
        raw_sink: Any | None = None,
    ) -> Catalog:
        catalog_summary = self.resolve_catalog(academic_year)
        catalog_id = _identifier(catalog_summary.get("_id"), "catalog id")
        catalog_raw = self.fetch_catalog(catalog_id)
        if _text(catalog_raw.get("_id")) != catalog_id:
            raise ValueError(f"Kuali catalog detail does not match requested id {catalog_id}")
        course_summaries = self.list_courses(catalog_id)
        program_summaries = self.list_programs(catalog_id)
        selected = (
            list(program_summaries)
            if selectors is None
            else self.select_programs(program_summaries, selectors)
        )
        course_record_index = self._course_record_index(course_summaries)

        if raw_sink:
            raw_sink("catalog-index.json", self.list_undergraduate_catalogs())
            raw_sink("catalog.json", catalog_raw)
            raw_sink("course-index.json", course_summaries)
            raw_sink("program-index.json", program_summaries)

        program_details = self._fetch_programs(catalog_id, selected, workers)
        for detail in program_details:
            if raw_sink:
                raw_sink(f"programs/{detail['pid']}.json", detail)

        if selectors is None:
            referenced_records = {
                source_record_id: code for code, source_record_id in course_record_index.items()
            }
        else:
            referenced_records: dict[str, str] = {}
            for detail in program_details:
                referenced_records.update(
                    self._resolve_course_references(
                        _text(detail.get("courseRequirementsNoUnits")), course_record_index
                    )
                )

        course_details: dict[str, dict[str, Any]] = {}
        frontier = dict(referenced_records)
        while frontier:
            if len(course_details) + len(frontier) > max_courses:
                raise ValueError(
                    f"Course dependency closure exceeded max_courses={max_courses}; "
                    "raise the limit after reviewing the source"
                )
            fetched = self._fetch_courses(catalog_id, frontier, workers)
            next_frontier: dict[str, str] = {}
            for source_record_id, detail in fetched.items():
                course_details[source_record_id] = detail
                if raw_sink:
                    raw_sink(f"courses/{source_record_id}.json", detail)
                for field_name in ("prerequisites", "corequisites", "antirequisites"):
                    next_frontier.update(
                        self._resolve_course_references(
                            _text(detail.get(field_name)), course_record_index
                        )
                    )
            frontier = {
                source_record_id: code
                for source_record_id, code in next_frontier.items()
                if source_record_id not in course_details
            }

        calendar = Calendar(
            academic_year=academic_year,
            title=_text(catalog_raw.get("title") or catalog_summary.get("title")),
            source="kuali",
            source_id=catalog_id,
            source_url=(
                "https://uwaterloo.ca/academic-calendar/undergraduate-studies/catalog"
                if academic_year == max(self.available_years())
                else "https://uwaterloo.ca/academic-calendar/undergraduate-studies/"
                f"catalog/archive/{academic_year}"
            ),
            starts_on=_text(catalog_raw.get("startDate") or catalog_summary.get("startDate")),
            ends_on=_text(catalog_raw.get("endDate") or catalog_summary.get("endDate")),
        )
        courses = tuple(
            sorted(
                (self._normalize_course(calendar, detail) for detail in course_details.values()),
                key=lambda course: course.course_code,
            )
        )
        programs = tuple(
            sorted(
                (self._normalize_program(calendar, detail) for detail in program_details),
                key=lambda program: program.title,
            )
        )
        quality = self._quality(courses, programs, set(course_record_index))
        return Catalog(
            generated_at=datetime.now(timezone.utc).isoformat(),
            calendar=calendar,
            courses=courses,
            programs=programs,
            quality=quality,
        )

    @staticmethod
    def _course_record_index(course_summaries: list[dict[str, Any]]) -> dict[str, str]:
        records_by_code: defaultdict[str, list[str]] = defaultdict(list)
        for summary in course_summaries:
            code = format_course_code(_text(summary.get("__catalogCourseId")))
            if not code:
                continue
            source_record_id = _identifier(summary.get("id"), "course record id")
            records_by_code[code].append(source_record_id)

        duplicates = sorted(code for code, records in records_by_code.items() if len(records) > 1)
        if duplicates:
            preview = ", ".join(duplicates[:10])
            raise ValueError(f"Kuali course index contains duplicate codes: {preview}")
        return {code: records[0] for code, records in records_by_code.items()}

    @staticmethod
    def _resolve_course_references(
        html: str, course_record_index: dict[str, str]
    ) -> dict[str, str]:
        references = extract_course_references(html)
        linked_codes = set(references.values())
        for code in extract_course_codes(html):
            source_record_id = course_record_index.get(code)
            if source_record_id and code not in linked_codes:
                references[source_record_id] = code
        return references

    def _fetch_programs(
        self,
        catalog_id: str,
        summaries: list[dict[str, Any]],
        workers: int,
    ) -> list[dict[str, Any]]:
        fetched: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            futures = {}
            for summary in summaries:
                program_id = _identifier(summary.get("pid"), "program pid")
                futures[executor.submit(self.fetch_program, catalog_id, program_id)] = program_id
            for future in as_completed(futures):
                program_id = futures[future]
                detail = future.result()
                if _text(detail.get("pid")) != program_id:
                    raise ValueError(
                        f"Kuali program detail does not match requested pid {program_id}"
                    )
                fetched.append(detail)
        return fetched

    def _fetch_courses(
        self, catalog_id: str, records: dict[str, str], workers: int
    ) -> dict[str, dict[str, Any]]:
        fetched: dict[str, dict[str, Any]] = {}
        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            futures = {
                executor.submit(self.fetch_course, catalog_id, source_record_id): source_record_id
                for source_record_id in sorted(records)
            }
            for future in as_completed(futures):
                source_record_id = futures[future]
                detail = future.result()
                if not detail:
                    raise ValueError(
                        f"Kuali returned an empty course record for {source_record_id} "
                        f"({records[source_record_id]})"
                    )
                if _text(detail.get("id")) != source_record_id:
                    raise ValueError(
                        f"Kuali course detail does not match requested id {source_record_id}"
                    )
                fetched[source_record_id] = detail
        return fetched

    @staticmethod
    def _normalize_course(calendar: Calendar, raw: dict[str, Any]) -> Course:
        source_course_code = _text(raw.get("__catalogCourseId"))
        course_code = format_course_code(source_course_code)
        parsed_subject, separator, parsed_number = course_code.partition(" ")
        subject = _name(raw.get("subjectCode")) or parsed_subject
        number = parsed_number if separator else source_course_code.removeprefix(subject)
        credits = raw.get("credits")
        units = None
        if isinstance(credits, dict):
            units = str(credits.get("value") or "") or None
        prerequisites_html = _text(raw.get("prerequisites"))
        corequisites_html = _text(raw.get("corequisites"))
        antirequisites_html = _text(raw.get("antirequisites"))
        source_record_id = _text(raw.get("id"))
        return Course(
            id=_text(raw.get("pid")),
            source_record_id=source_record_id,
            course_code=course_code,
            source_course_code=source_course_code,
            subject=subject,
            number=number,
            title=_text(raw.get("title")),
            description=_text(raw.get("description")),
            units=units,
            prerequisites_html=prerequisites_html,
            corequisites_html=corequisites_html,
            antirequisites_html=antirequisites_html,
            prerequisite_rule=parse_kuali_rules(prerequisites_html),
            corequisite_rule=parse_kuali_rules(corequisites_html),
            antirequisite_rule=parse_kuali_rules(antirequisites_html),
            source_url=f"{calendar.source_url}#/courses/view/{source_record_id}",
            source_hash=_canonical_hash(raw),
        )

    @staticmethod
    def _normalize_program(calendar: Calendar, raw: dict[str, Any]) -> Program:
        requirements_html = _text(raw.get("courseRequirementsNoUnits"))
        source_record_id = _text(raw.get("id"))
        return Program(
            id=_text(raw.get("pid")),
            source_record_id=source_record_id,
            code=_text(raw.get("code")),
            title=_text(raw.get("title")),
            credential_type=_name(raw.get("undergraduateCredentialType")),
            field_of_study=_name(raw.get("fieldOfStudy")),
            faculty=_name(raw.get("facultyCalendarDisplay")),
            requirements_html=requirements_html,
            requirement_rule=parse_kuali_rules(requirements_html),
            source_url=f"{calendar.source_url}#/programs/{raw.get('pid', '')}",
            source_hash=_canonical_hash(raw),
        )

    @staticmethod
    def _quality(
        courses: tuple[Course, ...],
        programs: tuple[Program, ...],
        active_course_codes: set[str],
    ) -> QualityReport:
        codes = [course.course_code for course in courses]
        duplicate_codes = tuple(sorted({code for code in codes if codes.count(code) > 1}))
        all_rules: list[Rule] = []
        for course in courses:
            for rule in (
                course.prerequisite_rule,
                course.corequisite_rule,
                course.antirequisite_rule,
            ):
                all_rules.extend(walk_rules(rule))
        for program in programs:
            all_rules.extend(walk_rules(program.requirement_rule))

        available_codes = set(codes)
        referenced_codes: set[str] = set()
        for course in courses:
            referenced_codes.update(referenced_course_codes(course.prerequisite_rule))
            referenced_codes.update(referenced_course_codes(course.corequisite_rule))
            referenced_codes.update(referenced_course_codes(course.antirequisite_rule))
        for program in programs:
            referenced_codes.update(referenced_course_codes(program.requirement_rule))

        dangling = tuple(sorted((referenced_codes & active_course_codes) - available_codes))
        external = tuple(sorted(referenced_codes - active_course_codes))
        warnings: list[str] = []
        if any(rule.type == "manual" for rule in all_rules):
            warnings.append(
                "Some rules require manual interpretation; inspect manual_rule_count before use."
            )
        if external:
            warnings.append(
                "Some rules reference courses outside the active catalog; "
                "inspect external_course_references before use."
            )
        return QualityReport(
            course_count=len(courses),
            program_count=len(programs),
            rule_count=len(all_rules),
            manual_rule_count=sum(rule.type == "manual" for rule in all_rules),
            duplicate_course_codes=duplicate_codes,
            dangling_course_references=dangling,
            external_course_references=external,
            warnings=tuple(warnings),
        )


class KualiSnapshotAdapter(KualiAdapter):
    """Rebuild normalized artifacts without making network requests."""

    def __init__(self, snapshot_root: Path) -> None:
        self.snapshot_root = snapshot_root.resolve()
        self._catalog_cache = None

    def _read(self, relative_path: str) -> JsonValue:
        path = (self.snapshot_root / relative_path).resolve()
        if not path.is_relative_to(self.snapshot_root):
            raise ValueError(f"Snapshot path escapes its root: {relative_path}")
        try:
            with path.open() as source:
                return json.load(source)
        except FileNotFoundError as error:
            raise ValueError(
                f"Raw snapshot is incomplete: missing {relative_path}. "
                "Create a new network snapshot with the current parser."
            ) from error

    def list_undergraduate_catalogs(self) -> list[dict[str, Any]]:
        return _objects(self._read("catalog-index.json"), "catalog list")

    def fetch_catalog(self, catalog_id: str) -> dict[str, Any]:
        return _object(self._read("catalog.json"), f"catalog {catalog_id}")

    def list_courses(self, catalog_id: str) -> list[dict[str, Any]]:
        return _objects(self._read("course-index.json"), f"course list {catalog_id}")

    def list_programs(self, catalog_id: str) -> list[dict[str, Any]]:
        return _objects(self._read("program-index.json"), f"program list {catalog_id}")

    def fetch_course(self, catalog_id: str, source_record_id: str) -> dict[str, Any]:
        return _object(
            self._read(f"courses/{source_record_id}.json"),
            f"course {source_record_id} in {catalog_id}",
        )

    def fetch_program(self, catalog_id: str, program_id: str) -> dict[str, Any]:
        return _object(
            self._read(f"programs/{program_id}.json"),
            f"program {program_id} in {catalog_id}",
        )
