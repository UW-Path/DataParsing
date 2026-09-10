from uwpath_data.rules import extract_course_codes, extract_course_references, parse_kuali_rules


def test_extract_course_references_normalizes_codes() -> None:
    html = '<a href="#/courses/view/abcdef0123456789">cs135</a>'

    assert extract_course_references(html) == {"abcdef0123456789": "CS 135"}


def test_extract_course_codes_finds_unlinked_compact_codes() -> None:
    text = "Must have completed at least 1 of CS135, BUS393W, or MATH 135."

    assert extract_course_codes(text) == ("CS 135", "BUS 393W", "MATH 135")


def test_extract_course_codes_does_not_treat_range_endpoints_as_courses() -> None:
    text = "Choose from CS340-CS398, CS 440-489, or MATH 135."

    assert extract_course_codes(text) == ("MATH 135",)


def test_parse_nested_kuali_rules() -> None:
    html = """
    <ul>
      <li>
        Complete all of the following:
        <ul>
          <li>
            Complete 1 of the following:
            <a href="#/courses/view/aa11">CS 135</a>
            <a href="#/courses/view/aa22">CS 145</a>
          </li>
          <li data-test="ruleView-courseRequirement">
            <a href="#/courses/view/aa33">MATH 135</a>
          </li>
        </ul>
      </li>
    </ul>
    """

    rule = parse_kuali_rules(html)

    assert rule is not None
    assert rule.type == "all"
    assert [child.type for child in rule.children] == ["at_least", "course"]
    assert rule.children[0].count == 1
    assert [child.course_code for child in rule.children[0].children] == ["CS 135", "CS 145"]
    assert rule.children[1].course_code == "MATH 135"


def test_untagged_kuali_choice_group_does_not_become_all() -> None:
    html = """
    <li>
      <span>Complete 1 of the following</span>
      <ul>
        <li data-test="ruleView-A.1"><div>Enrolled in an Honours program</div></li>
        <li data-test="ruleView-A.2"><div>Permission of the department</div></li>
      </ul>
    </li>
    """

    rule = parse_kuali_rules(html)

    assert rule is not None
    assert rule.type == "at_least"
    assert rule.count == 1
    assert [child.type for child in rule.children] == ["manual", "manual"]


def test_unstructured_text_is_preserved_as_manual_rule() -> None:
    rule = parse_kuali_rules("<p>Permission of the department is required.</p>")

    assert rule is not None
    assert rule.type == "manual"
    assert rule.reason == "no_structured_rules"
    assert rule.source_text == "Permission of the department is required."


def test_unlinked_course_choices_are_structured() -> None:
    rule = parse_kuali_rules("<p>Must have completed at least 1 of the following: CS135, CS145</p>")

    assert rule is not None
    assert rule.type == "at_least"
    assert rule.count == 1
    assert [child.course_code for child in rule.children] == ["CS 135", "CS 145"]
