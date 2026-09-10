from __future__ import annotations

import re
from collections.abc import Iterable

from bs4 import BeautifulSoup, Tag

from uwpath_data.models import Rule

COURSE_LINK_RE = re.compile(r"#/courses/view/([0-9a-f]+)")
COURSE_CODE_RE = re.compile(r"(?<![A-Z0-9])([A-Z]{2,8})\s*(\d{1,4}[A-Z]?)(?![A-Z0-9])")
COURSE_RANGE_RE = re.compile(
    r"\b[A-Z]{2,8}\s*\d{1,4}[A-Z]?\s*-\s*(?:[A-Z]{2,8}\s*)?\d{1,4}[A-Z]?\b"
)
COUNT_RE = re.compile(r"\b(?:complete|at least)\s+(\d+(?:\.\d+)?)\s+of\b", re.IGNORECASE)
RULE_TEST_RE = re.compile(r"^ruleView-")
OPERATOR_RE = re.compile(r"\bComplete\s+(?:all|\d+(?:\.\d+)?)\b", re.IGNORECASE)


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def format_course_code(value: str) -> str:
    compact = re.sub(r"\s+", "", value).upper()
    match = re.fullmatch(r"([A-Z]+)([0-9].*)", compact)
    return f"{match.group(1)} {match.group(2)}" if match else value.strip().upper()


def extract_course_references(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html or "", "html.parser")
    references: dict[str, str] = {}
    for link in soup.find_all("a", href=COURSE_LINK_RE):
        match = COURSE_LINK_RE.search(link.get("href", ""))
        if match:
            references[match.group(1)] = format_course_code(link.get_text(" ", strip=True))
    return references


def extract_course_codes(value: str) -> tuple[str, ...]:
    text = BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)
    text = COURSE_RANGE_RE.sub(" ", text)
    return tuple(
        dict.fromkeys(
            format_course_code(f"{match.group(1)}{match.group(2)}")
            for match in COURSE_CODE_RE.finditer(text)
        )
    )


def _header_text(item: Tag) -> str:
    clone = BeautifulSoup(str(item), "html.parser")
    clone_item = clone.find("li")
    if not clone_item:
        return ""
    for nested in clone_item.find_all("li"):
        nested.decompose()
    return normalize_text(clone_item.get_text(" ", strip=True))


def _is_rule_item(item: Tag) -> bool:
    data_test = item.get("data-test")
    return bool(
        (isinstance(data_test, str) and RULE_TEST_RE.match(data_test))
        or OPERATOR_RE.search(_header_text(item))
    )


def _nearest_rule_parent(item: Tag) -> Tag | None:
    return next(
        (parent for parent in item.find_parents("li") if _is_rule_item(parent)),
        None,
    )


def _direct_rule_children(rule_item: Tag) -> list[Tag]:
    return [
        candidate
        for candidate in rule_item.find_all("li")
        if _is_rule_item(candidate) and _nearest_rule_parent(candidate) is rule_item
    ]


def _own_text(rule_item: Tag) -> str:
    clone = BeautifulSoup(str(rule_item), "html.parser")
    clone_item = clone.find("li")
    if not clone_item:
        return ""
    for nested in _direct_rule_children(clone_item):
        nested.decompose()
    return normalize_text(clone_item.get_text(" ", strip=True))


def _operator(text: str, children: tuple[Rule, ...]) -> Rule:
    lowered = text.lower()
    if lowered.startswith("not completed") or lowered.startswith("not open"):
        return Rule(type="none_of", source_text=text, children=children)
    if (
        "complete all" in lowered
        or "completed the following" in lowered
        or "completed or concurrently enrolled in:" in lowered
    ):
        return Rule(type="all", source_text=text, children=children)
    count_match = COUNT_RE.search(text)
    if count_match:
        numeric_count = float(count_match.group(1))
        if numeric_count.is_integer():
            return Rule(
                type="at_least",
                source_text=text,
                count=int(numeric_count),
                children=children,
            )
    return Rule(
        type="manual",
        source_text=text,
        children=children,
        reason="unsupported_expression",
    )


def _parse_rule_item(rule_item: Tag) -> Rule:
    text = _own_text(rule_item)
    child_items = _direct_rule_children(rule_item)
    if child_items:
        return _operator(text, tuple(_parse_rule_item(child) for child in child_items))

    references = extract_course_references(str(rule_item))
    course_codes = tuple(dict.fromkeys((*references.values(), *extract_course_codes(text))))
    course_rules = tuple(
        Rule(type="course", source_text=code, course_code=code) for code in course_codes
    )
    if course_rules:
        if len(course_rules) == 1 and not (
            text.lower().startswith(("not completed", "not open")) or COUNT_RE.search(text)
        ):
            return course_rules[0]
        return _operator(text, course_rules)

    return Rule(type="manual", source_text=text, reason="unsupported_expression")


def parse_kuali_rules(html: str) -> Rule | None:
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    candidates = [candidate for candidate in soup.find_all("li") if _is_rule_item(candidate)]
    top_level = [candidate for candidate in candidates if _nearest_rule_parent(candidate) is None]

    if not top_level:
        text = normalize_text(soup.get_text(" ", strip=True))
        if not text:
            return None
        course_rules = tuple(
            Rule(type="course", source_text=code, course_code=code)
            for code in extract_course_codes(text)
        )
        if course_rules:
            return _operator(text, course_rules)
        return Rule(type="manual", source_text=text, reason="no_structured_rules")

    parsed = tuple(_parse_rule_item(item) for item in top_level)
    if len(parsed) == 1:
        return parsed[0]
    return Rule(type="all", source_text="Complete all top-level requirements", children=parsed)


def walk_rules(rule: Rule | None) -> Iterable[Rule]:
    if rule is None:
        return
    yield rule
    for child in rule.children:
        yield from walk_rules(child)


def referenced_course_codes(rule: Rule | None) -> set[str]:
    return {
        node.course_code
        for node in walk_rules(rule)
        if node.type == "course" and node.course_code is not None
    }
