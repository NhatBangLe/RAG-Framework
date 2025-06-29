from pydantic import ConfigDict, Field

from .base_model import BaseGoogleGenAIChatModel, BaseOllamaChatModel, BaseGoogleGenAIEmbeddings, \
    BaseHuggingFaceEmbeddings
from ..config.model.chat_model.google_genai import GoogleGenAILLMConfiguration
from ..config.model.chat_model.ollama import OllamaLLMConfiguration
from ..config.model.embeddings.google_genai import GoogleGenAIEmbeddingsConfiguration
from ..config.model.embeddings.hugging_face import HuggingFaceEmbeddingsConfiguration
from ..data.base_model import PyObjectId


class GoogleGenAIChatModelCreate(BaseGoogleGenAIChatModel):
    pass


class GoogleGenAIChatModelUpdate(BaseGoogleGenAIChatModel):
    pass


class GoogleGenAIChatModelPublic(GoogleGenAILLMConfiguration):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class GoogleGenAIEmbeddingsCreate(BaseGoogleGenAIEmbeddings):
    pass


class GoogleGenAIEmbeddingsUpdate(BaseGoogleGenAIEmbeddings):
    pass


class GoogleGenAIEmbeddingsPublic(GoogleGenAIEmbeddingsConfiguration):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class OllamaChatModelCreate(BaseOllamaChatModel):
    pass


class OllamaChatModelUpdate(BaseOllamaChatModel):
    pass


class OllamaChatModelPublic(OllamaLLMConfiguration):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class HuggingFaceEmbeddingsCreate(BaseHuggingFaceEmbeddings):
    pass


class HuggingFaceEmbeddingsUpdate(BaseHuggingFaceEmbeddings):
    pass


class HuggingFaceEmbeddingsPublic(HuggingFaceEmbeddingsConfiguration):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
