from pydantic import BaseModel, Field

from ...config.model.mcp import StreamableConnectionConfiguration, StdioConnectionConfiguration


class BasePrompt(BaseModel):
    suggest_questions_prompt: str = Field(min_length=8)
    respond_prompt: str = Field(min_length=11)


class BaseMCPServer(BaseModel):
    name: str = Field(description="Name of the server.", min_length=1)


class MCPStreamableServer(BaseMCPServer, StreamableConnectionConfiguration):
    pass


class MCPStdioServer(BaseMCPServer, StdioConnectionConfiguration):
    pass


SupportedMCPConfiguration = MCPStreamableServer | MCPStdioServer


class BaseMCP(BaseModel):
    servers: list[SupportedMCPConfiguration] = Field(min_length=1)
