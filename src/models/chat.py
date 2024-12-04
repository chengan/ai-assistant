from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    content: str = Field(..., description="用户输入的内容")
    provider_id: str = Field(..., description="内部模型ID")
    request_id: Optional[str] = Field(None, description="对话ID，用于继续对话")

class ChatResponse(BaseModel):
    code: int = Field(200, description="状态码")
    response: str = Field(..., description="AI回复内容")
    request_id: str = Field(..., description="对话ID") 