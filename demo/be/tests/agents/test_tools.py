from app.agents.tools import TOOL_ALLOWLISTS, run_allowed_tools


class TestAgentTools:
    def test_swing_diagnosis_allowlist(self, db_session, user_id: int) -> None:
        allowed = TOOL_ALLOWLISTS["swing_diagnosis"]
        assert "get_recent_swings" in allowed
        assert "search_golf_knowledge" in allowed

        results = run_allowed_tools(
            db_session,
            user_id=user_id,
            question_type="swing_diagnosis",
            query="slice driver",
        )
        assert "get_recent_swings" in results
        assert "search_golf_knowledge" in results
        assert "get_user_profile" not in results

    def test_unclear_calls_no_tools(self, db_session, user_id: int) -> None:
        results = run_allowed_tools(
            db_session,
            user_id=user_id,
            question_type="unclear",
            query="hello",
        )
        assert results == {}
