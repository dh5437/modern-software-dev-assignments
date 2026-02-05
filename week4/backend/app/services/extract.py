def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    items: list[str] = []
    tags: list[str] = []
    for line in lines:
        tokens = line.split()
        line_tags = [token for token in tokens if token.startswith("#") and len(token) > 1]
        if line_tags:
            tags.extend(line_tags)
        non_tag_tokens = [token for token in tokens if token not in line_tags]
        line_without_tags = " ".join(non_tag_tokens).strip()
        if line_without_tags.endswith("!") or line_without_tags.lower().startswith("todo:"):
            items.append(line_without_tags)
    return items + tags
