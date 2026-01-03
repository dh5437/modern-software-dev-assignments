# Week 2 Write-up

Tip: To preview this markdown file

- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: Jake Kim \
SUNet ID: 000000 \
Citations: 000000

This assignment took me about **TODO** hours to do.

## YOUR RESPONSES

For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature

Prompt:

```
Analyze the existing extract_action_items() function in week2/app/services/extract.py, which currently extracts action items using predefined heuristics.

Your task is to implement an LLM-powered alternative, extract_action_items_llm(), that utilizes Ollama to perform action item extraction via a large language model.

Some tips:

To produce structured outputs (i.e. JSON array of strings), refer to this:

Python
Using the Ollama Python library, pass in the schema as a JSON object to the format parameter as either dict or use Pydantic (recommended) to serialize the schema using model_json_schema().

from ollama import chat
from pydantic import BaseModel

class Country(BaseModel):
  name: str
  capital: str
  languages: list[str]

response = chat(
  messages=[
    {
      'role': 'user',
      'content': 'Tell me about Canada.',
    }
  ],
  model='llama3.1:8b',
  format=Country.model_json_schema(),
)

country = Country.model_validate_json(response.message.content)
print(country)
Output
name='Canada' capital='Ottawa' languages=['English', 'French']
```

Generated Code Snippets:

```
from pydantic import BaseModel

class ActionItems(BaseModel):
    """Pydantic model for structured LLM output containing action items."""
    items: List[str]


def extract_action_items_llm(text: str) -> List[str]:
    """
    LLM-powered action item extraction using Ollama.

    This function uses a large language model to extract action items from free-form text.
    It leverages structured outputs via Pydantic to ensure consistent JSON formatting.

    Args:
        text: The input text from which to extract action items.

    Returns:
        A list of extracted action items as strings. Returns an empty list if extraction fails
        or if no action items are found.
    """
    if not text or not text.strip():
        return []

    try:
        # Use Ollama chat API with structured output format
        response = chat(
            model='llama3.1:8b',  # Using a smaller model for efficiency
            messages=[
                {
                    'role': 'user',
                    'content': f"""Extract all action items, tasks, todos, and actionable items from the following text.
Return only the action items as a JSON array of strings. Each item should be a clear, concise action statement.
Remove any bullet points, numbering, or checkbox markers from the extracted items.

Text:
{text}

Extract and return only the actionable items.""",
                }
            ],
            format=ActionItems.model_json_schema(),
        )

        # Parse the structured response
        action_items_data = ActionItems.model_validate_json(response.message.content)

        # Deduplicate while preserving order (similar to the heuristic-based function)
        seen: set[str] = set()
        unique: List[str] = []
        for item in action_items_data.items:
            cleaned = item.strip()
            if not cleaned:
                continue
            lowered = cleaned.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            unique.append(cleaned)

        return unique

    except Exception as e:
        # Log error and return empty list as fallback
        # In production, you might want to log this to a proper logging system
        print(f"Error in extract_action_items_llm: {e}")
        return []
```

### Exercise 2: Add Unit Tests

Prompt:

```
Write unit tests for extract_action_items_llm() covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) in week2/tests/test_extract.py.
```

Generated Code Snippets:

```
4
from ..app.services.extract import extract_action_items, extract_action_items_llm

22~143
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
```

### Exercise 3: Refactor Existing Code for Clarity

Prompt:

```
TODO
```

Generated/Modified Code Snippets:

```
TODO: List all modified code files with the relevant line numbers. (We anticipate there may be multiple scattered changes here – just produce as comprehensive of a list as you can.)
```

### Exercise 4: Use Agentic Mode to Automate a Small Task

Prompt:

```
TODO
```

Generated Code Snippets:

```
TODO: List all modified code files with the relevant line numbers.
```

### Exercise 5: Generate a README from the Codebase

Prompt:

```
TODO
```

Generated Code Snippets:

```
TODO: List all modified code files with the relevant line numbers.
```

## SUBMISSION INSTRUCTIONS

1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields.
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope.
