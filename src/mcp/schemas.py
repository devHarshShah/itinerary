from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# MCP Protocol Model Definitions
class MCPRequestContext(BaseModel):
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    system_prompt: Optional[str] = None

class MCPGenerateRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class MCPContent(BaseModel):
    type: str = "text"
    text: str

class MCPMessage(BaseModel):
    role: str
    content: List[MCPContent]

class MCPCompletionResponse(BaseModel):
    id: str
    model: str
    object: str = "completion"
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]