from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Calendar:
    academic_year: str
    title: str
    source: str
    source_id: str
    source_url: str
    starts_on: str
    ends_on: str


@dataclass(frozen=True)
class Rule:
    type: str
    source_text: str
    children: tuple[Rule, ...] = ()
    count: int | None = None
    course_code: str | None = None
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "type": self.type,
            "source_text": self.source_text,
        }
        if self.children:
            data["children"] = [child.to_dict() for child in self.children]
        if self.count is not None:
            data["count"] = self.count
        if self.course_code is not None:
            data["course_code"] = self.course_code
        if self.reason is not None:
            data["reason"] = self.reason
        return data


@dataclass(frozen=True)
class Course:
    id: str
    source_record_id: str
    course_code: str
    source_course_code: str
    subject: str
    number: str
    title: str
    description: str
    units: str | None
    prerequisites_html: str
    corequisites_html: str
    antirequisites_html: str
    prerequisite_rule: Rule | None
    corequisite_rule: Rule | None
    antirequisite_rule: Rule | None
    source_url: str
    source_hash: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for field_name in (
            "prerequisite_rule",
            "corequisite_rule",
            "antirequisite_rule",
        ):
            rule = getattr(self, field_name)
            data[field_name] = rule.to_dict() if rule else None
        return data


@dataclass(frozen=True)
class Program:
    id: str
    source_record_id: str
    code: str
    title: str
    credential_type: str
    field_of_study: str
    faculty: str
    requirements_html: str
    requirement_rule: Rule | None
    source_url: str
    source_hash: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["requirement_rule"] = (
            self.requirement_rule.to_dict() if self.requirement_rule else None
        )
        return data


@dataclass(frozen=True)
class QualityReport:
    course_count: int
    program_count: int
    rule_count: int
    manual_rule_count: int
    duplicate_course_codes: tuple[str, ...] = ()
    dangling_course_references: tuple[str, ...] = ()
    external_course_references: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def publishable(self) -> bool:
        return not self.duplicate_course_codes and not self.dangling_course_references

    @property
    def planner_ready(self) -> bool:
        return self.publishable and self.manual_rule_count == 0


@dataclass(frozen=True)
class Catalog:
    generated_at: str
    calendar: Calendar
    courses: tuple[Course, ...]
    programs: tuple[Program, ...]
    quality: QualityReport
    schema_version: int = field(default=SCHEMA_VERSION, init=False)

    def to_dict(self) -> dict[str, Any]:
        quality = asdict(self.quality)
        for field_name in (
            "duplicate_course_codes",
            "dangling_course_references",
            "external_course_references",
            "warnings",
        ):
            quality[field_name] = list(quality[field_name])
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "calendar": asdict(self.calendar),
            "courses": [course.to_dict() for course in self.courses],
            "programs": [program.to_dict() for program in self.programs],
            "quality": {
                **quality,
                "publishable": self.quality.publishable,
                "planner_ready": self.quality.planner_ready,
            },
        }
