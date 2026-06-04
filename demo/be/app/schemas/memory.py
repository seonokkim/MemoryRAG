from pydantic import BaseModel


class MemoryItem(BaseModel):
    id: int
    memory_type: str
    content: str
    confidence: float | None

    model_config = {"from_attributes": True}
