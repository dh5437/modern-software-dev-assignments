import re


_PREFIX_RE = re.compile(r"^(todo|action|fixme|next)\s*[:\-]\s*", re.IGNORECASE)
_CHECKBOX_RE = re.compile(r"^\[( |x|X)\]\s*")
_IMPERATIVE_RE = re.compile(
    r"^(please|remember to|we should|we need to|need to|must|don't forget to)\b",
    re.IGNORECASE,
)


def _normalize_line(raw_line: str) -> str:
    line = raw_line.strip()
    line = line.lstrip("-*• ").strip()
    return line


def extract_action_items(text: str) -> list[str]:
    results: list[str] = []
    for raw_line in text.splitlines():
        if not raw_line.strip():
            continue
        line = _normalize_line(raw_line)
        if not line:
            continue

        checkbox_match = _CHECKBOX_RE.match(line)
        if checkbox_match:
            if checkbox_match.group(1).lower() == "x":
                continue
            line = _CHECKBOX_RE.sub("", line, count=1).strip()
            if line:
                results.append(line)
            continue

        if _PREFIX_RE.match(line):
            results.append(line)
            continue

        if _IMPERATIVE_RE.match(line):
            results.append(line)
            continue

        normalized = line.lower()
        if normalized.startswith("todo") or normalized.startswith("action"):
            results.append(line)
            continue

        if line.endswith("!"):
            results.append(line)

    return results

