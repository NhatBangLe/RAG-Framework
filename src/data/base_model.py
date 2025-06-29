from typing import Annotated

from pydantic import BeforeValidator, BaseModel, Field

from src.config.model.chat_model.google_genai import HarmCategory, HarmBlockThreshold
from src.config.model.embeddings.google_genai import GoogleGenAIEmbeddingsTaskType

PyObjectId = Annotated[str, BeforeValidator(str)]


class BaseGoogleGenAIChatModel(BaseModel):
    model_name: str = Field(min_length=1)
    temperature: float = Field(default=0.5, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=10)
    max_retries: int = Field(default=6, ge=0)
    timeout: float | None = Field(default=None, ge=0.0)
    top_k: int | None = Field(default=None, ge=0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    safety_settings: dict[HarmCategory, HarmBlockThreshold] | None = Field(default=None)


class BaseGoogleGenAIEmbeddings(BaseModel):
    name: str
    model_name: str = Field(min_length=1)
    task_type: GoogleGenAIEmbeddingsTaskType | None = Field(default=None)


class BaseOllamaChatModel(BaseModel):
    model_name: str = Field(min_length=1)
    temperature: float = Field(default=0.8, ge=0.0, le=1.0)
    base_url: str | None = Field(default=None, min_length=1)
    seed: int | None = Field(default=None)
    num_ctx: int = Field(default=2048)
    num_predict: int | None = Field(default=128)
    repeat_penalty: float | None = Field(default=1.1)
    top_k: int | None = Field(default=40, ge=0)
    top_p: float | None = Field(default=0.9, ge=0.0, le=1.0)
    stop: list[str] | None = Field(default=None)


class BaseHuggingFaceEmbeddings(BaseModel):
    name: str
    model_name: str = Field(min_length=1)
