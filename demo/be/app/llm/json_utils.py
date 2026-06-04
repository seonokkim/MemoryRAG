import json
import re
from typing import Any


def extract_json_block(text: str) -> str:
    """Pull JSON from raw model text (fenced block or first object/array)."""
    stripped = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", stripped, re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    pairs = ("[", "]") if stripped.startswith("[") else ("{", "}")
    start = stripped.find(pairs[0])
    end = stripped.rfind(pairs[1])
    if start != -1 and end > start:
        return stripped[start : end + 1]
    return stripped


def parse_json_object(text: str) -> dict[str, Any] | None:
    try:
        data = json.loads(extract_json_block(text))
    except (json.JSONDecodeError, TypeError):
        return None
    return data if isinstance(data, dict) else None


def parse_json_array(text: str) -> list[Any] | None:
    try:
        data = json.loads(extract_json_block(text))
    except (json.JSONDecodeError, TypeError):
        return None
    return data if isinstance(data, list) else None
