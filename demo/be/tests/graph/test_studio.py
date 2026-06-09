"""LangGraph Studio entrypoint — must expose the real coach workflow."""

from app.graph.studio import COACH_GRAPH_NODES, STUDIO_SAMPLE_INPUT, graph


class TestStudioEntrypoint:
    def test_exports_compiled_graph(self) -> None:
        assert graph is not None
        assert hasattr(graph, "invoke")

    def test_coach_graph_has_sixteen_nodes(self) -> None:
        assert len(COACH_GRAPH_NODES) == 16
        node_names = set(graph.get_graph().nodes.keys())
        for name in COACH_GRAPH_NODES:
            assert name in node_names, f"missing node {name}"

    def test_studio_sample_input_has_required_fields(self) -> None:
        assert STUDIO_SAMPLE_INPUT["user_id"] == 1
        assert STUDIO_SAMPLE_INPUT["user_message"]
        assert STUDIO_SAMPLE_INPUT["trace_id"]
        assert "retry_count" in STUDIO_SAMPLE_INPUT
