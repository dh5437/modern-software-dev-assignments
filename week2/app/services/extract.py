from __future__ import annotations

import re
from typing import List

from ollama import chat
from pydantic import BaseModel

from ..config import settings

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


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
            model=settings.ollama_model,
            messages=[
                {
                    'role': 'user',
                    'content': f"""From the following text, extract only those items that:
- Contain one of the words "todo:", "action:", or "next:" (case-insensitive), OR
- Are presented as bullet points or numbered lists.

NEVER mind about the meanings of the items. Answer in the same language as the input text.
Return ONLY those items as a JSON array of strings. Each extracted item should be a clear, concise action statement with any bullet points, numbering, or checkbox markers removed.

Do NOT extract or return any items that do not meet these criteria.

Text:
{text}

Extract and return only the actionable items as specified above.""",
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
