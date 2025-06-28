from typing import Literal

from pydantic import ConfigDict, Field

from ..config.model.chat_model.google_genai import GoogleGenAILLMConfiguration
from ..config.model.chat_model.ollama import OllamaLLMConfiguration
from ..data.base_model import PyObjectId


class GoogleGenAIChatModelCreate(GoogleGenAILLMConfiguration):
    provider: Literal["google_genai"] = Field(default="google_genai")


class GoogleGenAIChatModelPublic(GoogleGenAILLMConfiguration):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class OllamaChatModelCreate(OllamaLLMConfiguration):
    provider: Literal["google_genai"] = Field(default="ollama")


class OllamaChatModelPublic(OllamaLLMConfiguration):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
