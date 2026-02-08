from backend.app.services.extract import extract_action_items


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - ACTION: review PR
    - FIXME: fix flaky test
    - [ ] follow up with team
    - [x] already done
    Please update the docs
    We should tighten validation
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "ACTION: review PR" in items
    assert "FIXME: fix flaky test" in items
    assert "follow up with team" in items
    assert "Please update the docs" in items
    assert "We should tighten validation" in items
    assert "Ship it!" in items

