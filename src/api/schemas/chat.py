from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="用户问题",
    )
    session_id: str | None = Field(
        None,
        description="会话ID，不传则创建新会话",
    )


class ChatResponse(BaseModel):
    answer: str = Field(..., description="完整回答（非流式场景）")
    session_id: str = Field(..., description="会话ID")
