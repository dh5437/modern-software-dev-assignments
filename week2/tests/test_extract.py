import os
import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# Tests for extract_action_items_llm()
def test_extract_action_items_llm_empty_input():
    """Test that empty input returns empty list."""
    items = extract_action_items_llm("")
    assert items == []
    
    items = extract_action_items_llm("   ")
    assert items == []


def test_extract_action_items_llm_bullet_lists():
    """Test extraction from bullet point lists."""
    text = """
    Meeting notes:
    - Set up database connection
    - Implement authentication
    - Write unit tests
    - Deploy to production
    """.strip()
    
    items = extract_action_items_llm(text)
    assert len(items) > 0
    # LLM should extract action items from bullet points
    assert isinstance(items, list)
    assert all(isinstance(item, str) for item in items)


def test_extract_action_items_llm_keyword_prefixed():
    """Test extraction from keyword-prefixed lines."""
    text = """
    Action items:
    todo: Review code changes
    action: Update documentation
    next: Schedule team meeting
    """.strip()
    
    items = extract_action_items_llm(text)
    assert len(items) > 0
    assert isinstance(items, list)


def test_extract_action_items_llm_checkboxes():
    """Test extraction from checkbox-style items."""
    text = """
    Project tasks:
    [ ] Fix bug in login system
    [ ] Add error handling
    [todo] Update API documentation
    """.strip()
    
    items = extract_action_items_llm(text)
    assert len(items) > 0
    assert isinstance(items, list)


def test_extract_action_items_llm_mixed_format():
    """Test extraction from mixed format text."""
    text = """
    Weekly planning meeting notes:
    
    We discussed several action items:
    - First, we need to refactor the database layer
    - Then, implement the new API endpoint
    todo: Write integration tests
    action: Update frontend components
    
    Also remember to:
    1. Review pull requests
    2. Update deployment scripts
    
    Some narrative text that is not an action item.
    """.strip()
    
    items = extract_action_items_llm(text)
    assert len(items) > 0
    assert isinstance(items, list)
    # Should extract multiple action items
    assert len(items) >= 3


def test_extract_action_items_llm_narrative_only():
    """Test that narrative text without action items returns empty or minimal results."""
    text = """
    This is a meeting summary. We discussed various topics including
    the current state of the project and future plans. The team
    is working well together and making good progress.
    """.strip()
    
    items = extract_action_items_llm(text)
    # LLM might extract some items or return empty, both are acceptable
    assert isinstance(items, list)


def test_extract_action_items_llm_imperative_sentences():
    """Test extraction from imperative sentences."""
    text = """
    Create a new user interface component.
    Implement the authentication flow.
    Write comprehensive tests for the new feature.
    Deploy the application to staging environment.
    """.strip()
    
    items = extract_action_items_llm(text)
    assert len(items) > 0
    assert isinstance(items, list)


def test_extract_action_items_llm_deduplication():
    """Test that duplicate action items are removed."""
    text = """
    - Set up database
    - Set up database
    - Implement API
    - Implement API
    """.strip()
    
    items = extract_action_items_llm(text)
    # Should have deduplication logic
    assert isinstance(items, list)
    # Check that items are unique (case-insensitive)
    lower_items = [item.lower() for item in items]
    assert len(lower_items) == len(set(lower_items))
