import pytest

from app.core.config import Settings
from app.llm.vertex_ai_client import VertexAIClient, VertexConfigurationError


class TestVertexAIClientConfig:
    def test_missing_project_id_raises(self) -> None:
        with pytest.raises(RuntimeError, match="VERTEX_PROJECT_ID"):
            VertexAIClient(Settings(llm_provider="vertex", vertex_project_id=""))

    def test_accepts_project_id_without_network(self) -> None:
        client = VertexAIClient(
            Settings(
                llm_provider="vertex",
                vertex_project_id="demo-project",
                vertex_location="us-central1",
                vertex_model_name="gemini-1.5-flash",
            )
        )
        assert client.project_id == "demo-project"


@pytest.mark.skip(
    reason="Manual integration: requires pip install -r requirements-optional.txt, "
    "VERTEX_PROJECT_ID, and GCP credentials. No network in CI."
)
def test_vertex_real_coach_chat_manual() -> None:
    """Run manually: LLM_PROVIDER=vertex + seeded MySQL + POST /api/coach/chat."""
    raise NotImplementedError("Use scripts/smoke_vertex_chat.py after manual GCP setup")
