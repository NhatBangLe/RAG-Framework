from pydantic import Field, ConfigDict

from src.config.model.embeddings.google_genai import GoogleGenAIEmbeddingsConfiguration
from src.config.model.embeddings.hugging_face import HuggingFaceEmbeddingsConfiguration
from src.data import PyObjectId


class GoogleGenAIEmbeddings(GoogleGenAIEmbeddingsConfiguration):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class HuggingFaceEmbeddings(HuggingFaceEmbeddingsConfiguration):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
