from app.llm.json_utils import extract_json_block, parse_json_array, parse_json_object


class TestVertexJsonUtils:
    def test_parse_object_from_fence(self) -> None:
        raw = 'Here is the answer:\n```json\n{"summary": "ok", "confidence": 0.9}\n```'
        data = parse_json_object(raw)
        assert data is not None
        assert data["summary"] == "ok"
        assert data["confidence"] == 0.9

    def test_parse_array_inline(self) -> None:
        raw = '[{"memory_type": "user_goal", "content": "Reduce slice", "confidence": 0.8}]'
        data = parse_json_array(raw)
        assert data is not None
        assert len(data) == 1

    def test_invalid_json_returns_none(self) -> None:
        assert parse_json_object("not json at all") is None
        assert extract_json_block("not json") == "not json"
