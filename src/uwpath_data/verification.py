from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import ValidationError

from uwpath_data.artifacts import validate_catalog


class VerificationError(ValueError):
    pass


def _read_object(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as source:
            value = json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        raise VerificationError(f"Could not read JSON object {path}: {error}") from error
    if not isinstance(value, dict):
        raise VerificationError(f"Expected a JSON object in {path}")
    return value


def _read_array(path: Path) -> list[Any]:
    try:
        with path.open(encoding="utf-8") as source:
            value = json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        raise VerificationError(f"Could not read JSON array {path}: {error}") from error
    if not isinstance(value, list):
        raise VerificationError(f"Expected a JSON array in {path}")
    return value


def load_catalog(path: Path) -> dict[str, Any]:
    catalog_path = path / "catalog.json" if path.is_dir() else path
    catalog = _read_object(catalog_path)
    try:
        validate_catalog(catalog)
    except ValidationError as error:
        location = ".".join(str(part) for part in error.absolute_path) or "root"
        raise VerificationError(f"Catalog schema failed at {location}: {error.message}") from error
    return catalog


def _rule_counts(catalog: dict[str, Any]) -> tuple[int, int]:
    count = 0
    manual_count = 0
    stack = []
    for course in catalog["courses"]:
        stack.extend(
            rule
            for rule in (
                course["prerequisite_rule"],
                course["corequisite_rule"],
                course["antirequisite_rule"],
            )
            if rule is not None
        )
    stack.extend(
        program["requirement_rule"]
        for program in catalog["programs"]
        if program["requirement_rule"] is not None
    )
    while stack:
        rule = stack.pop()
        count += 1
        manual_count += rule["type"] == "manual"
        stack.extend(rule.get("children", []))
    return count, manual_count


def verify_catalog_directory(root: Path) -> dict[str, Any]:
    manifest = _read_object(root / "manifest.json")
    catalog = load_catalog(root)
    courses = _read_array(root / "courses.json")
    programs = _read_array(root / "programs.json")

    if courses != catalog["courses"]:
        raise VerificationError("courses.json does not match the catalog projection")
    if programs != catalog["programs"]:
        raise VerificationError("programs.json does not match the catalog projection")

    quality = catalog["quality"]
    rule_count, manual_rule_count = _rule_counts(catalog)
    expected_counts = {
        "course_count": len(courses),
        "program_count": len(programs),
        "rule_count": rule_count,
        "manual_rule_count": manual_rule_count,
    }
    for field_name, expected in expected_counts.items():
        if quality[field_name] != expected:
            raise VerificationError(f"quality field {field_name!r} should be {expected}")
    expected_publishable = (
        not quality["duplicate_course_codes"] and not quality["dangling_course_references"]
    )
    if quality["publishable"] is not expected_publishable:
        raise VerificationError("quality field 'publishable' is inconsistent")
    if quality["planner_ready"] is not (expected_publishable and quality["manual_rule_count"] == 0):
        raise VerificationError("quality field 'planner_ready' is inconsistent")

    expected_metadata = {
        "schema_version": catalog["schema_version"],
        "academic_year": catalog["calendar"]["academic_year"],
        "generated_at": catalog["generated_at"],
        "source": catalog["calendar"]["source"],
        "source_id": catalog["calendar"]["source_id"],
        "quality": catalog["quality"],
    }
    for field_name, expected in expected_metadata.items():
        if manifest.get(field_name) != expected:
            raise VerificationError(f"manifest field {field_name!r} does not match catalog.json")

    file_metadata = manifest.get("files")
    if not isinstance(file_metadata, dict):
        raise VerificationError("manifest files must be an object")
    for filename in ("catalog.json", "courses.json", "programs.json"):
        metadata = file_metadata.get(filename)
        if not isinstance(metadata, dict):
            raise VerificationError(f"manifest is missing metadata for {filename}")
        try:
            payload = (root / filename).read_bytes()
        except OSError as error:
            raise VerificationError(f"Could not read {root / filename}: {error}") from error
        if metadata.get("bytes") != len(payload):
            raise VerificationError(f"manifest byte count does not match {filename}")
        if metadata.get("sha256") != hashlib.sha256(payload).hexdigest():
            raise VerificationError(f"manifest hash does not match {filename}")

    build = manifest.get("build")
    if build is not None:
        if not isinstance(build, dict):
            raise VerificationError("manifest build must be an object")
        if build.get("scope") not in {"full_catalog", "program_slice"}:
            raise VerificationError("manifest build scope is invalid")
        selectors = build.get("program_selectors")
        if not isinstance(selectors, list) or not all(
            isinstance(selector, str) and selector for selector in selectors
        ):
            raise VerificationError("manifest build program_selectors are invalid")
        if build["scope"] == "full_catalog" and selectors:
            raise VerificationError("full-catalog manifest must not have program selectors")
        if build["scope"] == "program_slice" and not selectors:
            raise VerificationError("program-slice manifest must have program selectors")
        if not isinstance(build.get("raw_snapshot"), bool):
            raise VerificationError("manifest build raw_snapshot must be boolean")

    result = {
        "valid": True,
        "academic_year": catalog["calendar"]["academic_year"],
        "course_count": len(courses),
        "program_count": len(programs),
        "publishable": catalog["quality"]["publishable"],
        "planner_ready": catalog["quality"]["planner_ready"],
    }
    if build is not None:
        result["build"] = build
    return result
