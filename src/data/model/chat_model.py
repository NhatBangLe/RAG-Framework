from pydantic import Field, ConfigDict

from src.config.model.chat_model.google_genai import GoogleGenAILLMConfiguration
from src.config.model.chat_model.ollama import OllamaLLMConfiguration
from src.data import PyObjectId


class GoogleGenAIChatModel(GoogleGenAILLMConfiguration):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class OllamaChatModel(OllamaLLMConfiguration):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
