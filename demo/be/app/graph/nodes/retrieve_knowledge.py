from sqlalchemy.orm import Session

from app.graph.state import CoachState
from app.rag.knowledge_index import KnowledgeIndexService


def retrieve_knowledge(state: CoachState, db: Session) -> dict:
    index = KnowledgeIndexService(db)
    query = state.get("rewritten_query") or state["user_message"]
    chunks = index.query(query, top_k=5)
    payload = [
        {"content": c.content, "score": c.score, "metadata": c.metadata}
        for c in chunks
    ]
    trace = dict(state.get("trace") or {})
    trace["retrieve_knowledge"] = {"chunk_count": len(payload)}
    failure = state.get("failure_type")
    if len(payload) == 0:
        failure = failure or "low_retrieval_score"
    return {
        "golf_knowledge_chunks": payload,
        "trace": trace,
        "failure_type": failure,
        "retrieved_chunk_count": len(payload),
    }
