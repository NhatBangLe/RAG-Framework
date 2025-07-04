from pydantic import Field, ConfigDict

from ...config.model.embeddings.google_genai import GoogleGenAIEmbeddingsConfiguration
from ...config.model.embeddings.hugging_face import HuggingFaceEmbeddingsConfiguration
from .. import PyObjectId
from ...data.base_model.embeddings import BaseGoogleGenAIEmbeddings, BaseHuggingFaceEmbeddings


class GoogleGenAIEmbeddingsCreate(BaseGoogleGenAIEmbeddings):
    pass


class GoogleGenAIEmbeddingsUpdate(BaseGoogleGenAIEmbeddings):
    pass


class GoogleGenAIEmbeddingsPublic(GoogleGenAIEmbeddingsConfiguration):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class HuggingFaceEmbeddingsCreate(BaseHuggingFaceEmbeddings):
    pass


class HuggingFaceEmbeddingsUpdate(BaseHuggingFaceEmbeddings):
    pass


class HuggingFaceEmbeddingsPublic(HuggingFaceEmbeddingsConfiguration):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
