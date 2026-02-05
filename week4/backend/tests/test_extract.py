from backend.app.services.extract import extract_action_items


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable #later
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items
    assert "#later" in items


def test_extract_only_tags_line():
    text = """
    #alpha #beta
    """.strip()
    items = extract_action_items(text)
    assert "#alpha" in items
    assert "#beta" in items
