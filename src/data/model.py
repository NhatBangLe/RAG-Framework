from pydantic import Field, ConfigDict

from ..config.model.chat_model.google_genai import GoogleGenAILLMConfiguration
from ..config.model.chat_model.ollama import OllamaLLMConfiguration
from ..config.model.embeddings.google_genai import GoogleGenAIEmbeddingsConfiguration
from ..config.model.embeddings.hugging_face import HuggingFaceEmbeddingsConfiguration
from ..config.model.prompt import PromptConfiguration
from ..data.base_model import PyObjectId


class GoogleGenAIChatModel(GoogleGenAILLMConfiguration):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class GoogleGenAIEmbeddings(GoogleGenAIEmbeddingsConfiguration):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class OllamaChatModel(OllamaLLMConfiguration):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class HuggingFaceEmbeddings(HuggingFaceEmbeddingsConfiguration):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class Prompt(PromptConfiguration):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
