import json
from typing import Any


def safe_json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)
