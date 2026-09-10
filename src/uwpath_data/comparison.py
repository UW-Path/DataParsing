from __future__ import annotations

from pathlib import Path
from typing import Any

from uwpath_data.verification import VerificationError, load_catalog


def _index(records: list[dict[str, Any]], field_name: str, label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        key = record.get(field_name)
        if not isinstance(key, str) or not key:
            raise VerificationError(f"{label} has no {field_name}")
        if key in indexed:
            raise VerificationError(f"Duplicate {label} {field_name}: {key}")
        indexed[key] = record
    return indexed


def _record_delta(
    baseline: list[dict[str, Any]],
    candidate: list[dict[str, Any]],
    *,
    key: str,
    label: str,
) -> dict[str, Any]:
    before = _index(baseline, key, label)
    after = _index(candidate, key, label)
    before_keys = set(before)
    after_keys = set(after)
    changed = sorted(
        record_key
        for record_key in before_keys & after_keys
        if before[record_key]["source_hash"] != after[record_key]["source_hash"]
    )
    count_delta = len(after) - len(before)
    count_delta_percent = None
    if before:
        count_delta_percent = round((count_delta / len(before)) * 100, 2)
    return {
        "baseline_count": len(before),
        "candidate_count": len(after),
        "count_delta": count_delta,
        "count_delta_percent": count_delta_percent,
        "added": sorted(after_keys - before_keys),
        "removed": sorted(before_keys - after_keys),
        "changed": changed,
    }


def compare_catalogs(
    baseline_path: Path,
    candidate_path: Path,
    *,
    max_course_drop_percent: float = 10,
    max_program_drop_percent: float = 10,
    max_manual_rule_increase: int | None = None,
    require_planner_ready: bool = False,
) -> dict[str, Any]:
    if max_course_drop_percent < 0 or max_program_drop_percent < 0:
        raise VerificationError("count-drop thresholds must not be negative")
    if max_manual_rule_increase is not None and max_manual_rule_increase < 0:
        raise VerificationError("manual-rule threshold must not be negative")
    baseline = load_catalog(baseline_path)
    candidate = load_catalog(candidate_path)
    courses = _record_delta(
        baseline["courses"], candidate["courses"], key="course_code", label="course"
    )
    programs = _record_delta(
        baseline["programs"], candidate["programs"], key="code", label="program"
    )

    baseline_quality = baseline["quality"]
    candidate_quality = candidate["quality"]
    manual_delta = candidate_quality["manual_rule_count"] - baseline_quality["manual_rule_count"]
    failures: list[str] = []
    if not candidate_quality["publishable"]:
        failures.append("candidate catalog is not publishable")
    if courses["count_delta_percent"] is not None:
        course_drop = -courses["count_delta_percent"]
        if course_drop > max_course_drop_percent:
            failures.append(
                f"course count dropped {course_drop:.2f}%, above {max_course_drop_percent:.2f}%"
            )
    if programs["count_delta_percent"] is not None:
        program_drop = -programs["count_delta_percent"]
        if program_drop > max_program_drop_percent:
            failures.append(
                f"program count dropped {program_drop:.2f}%, above {max_program_drop_percent:.2f}%"
            )
    if max_manual_rule_increase is not None and manual_delta > max_manual_rule_increase:
        failures.append(
            f"manual rule count increased by {manual_delta}, above {max_manual_rule_increase}"
        )
    if require_planner_ready and not candidate_quality["planner_ready"]:
        failures.append("candidate catalog is not planner-ready")

    return {
        "baseline_year": baseline["calendar"]["academic_year"],
        "candidate_year": candidate["calendar"]["academic_year"],
        "courses": courses,
        "programs": programs,
        "quality": {
            "baseline_manual_rule_count": baseline_quality["manual_rule_count"],
            "candidate_manual_rule_count": candidate_quality["manual_rule_count"],
            "manual_rule_count_delta": manual_delta,
            "candidate_publishable": candidate_quality["publishable"],
            "candidate_planner_ready": candidate_quality["planner_ready"],
        },
        "gates": {"passed": not failures, "failures": failures},
    }
