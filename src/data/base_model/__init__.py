import datetime

from pydantic import BaseModel, Field, field_validator

from ...config.model.mcp import StreamableConnectionConfiguration, StdioConnectionConfiguration
from ...util.constant import SUPPORTED_LANGUAGE_DICT
from ...util.function import get_datetime_now


# noinspection PyNestedDecorators
class BaseAgent(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    language: str = Field(description="Supported languages: vi, en")
    image_recognizer_id: str = Field(description="Image recognizer configuration ID", min_length=1)
    retriever_ids: list[str] = Field(description="Retriever configuration IDs", min_length=1)
    tool_ids: list[str] | None = Field(description="Tool configuration IDs", default=None)
    mcp_server_ids: list[str] | None = Field(description="MCP configuration IDs", default=None, min_length=1)
    llm_id: str = Field(description="Chat model configuration ID")
    prompt_id: str = Field(description="Prompt configuration ID")

    @field_validator("language", mode="after")
    @classmethod
    def validate_language(cls, v: str):
        if v not in SUPPORTED_LANGUAGE_DICT:
            raise ValueError(f'Unsupported {v} language.')
        return v


class BasePrompt(BaseModel):
    name: str = Field(min_length=1)
    respond_prompt: str = Field(
        min_length=1,
        description="A prompt is used for instructing LLM to generate answers.")


class BaseMCPServer(BaseModel):
    name: str = Field(description="Name of the server.", min_length=1)


class BaseMCPStreamableServer(BaseMCPServer, StreamableConnectionConfiguration):
    pass


class BaseMCPStdioServer(BaseMCPServer, StdioConnectionConfiguration):
    pass


class BaseFile(BaseModel):
    name: str = Field(description="Name of the file.", min_length=1)
    path: str = Field(description="Path to the file.", min_length=1)
    mime_type: str | None = Field(default=None, description="MIME type of the file.", min_length=1)
    created_at: datetime.datetime = Field(default_factory=get_datetime_now)
