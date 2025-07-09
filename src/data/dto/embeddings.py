from pydantic import Field, ConfigDict

from .. import PyObjectId
from ...data.base_model.embeddings import BaseGoogleGenAIEmbeddings, BaseHuggingFaceEmbeddings


class GoogleGenAIEmbeddingsCreate(BaseGoogleGenAIEmbeddings):
    pass


class GoogleGenAIEmbeddingsUpdate(BaseGoogleGenAIEmbeddings):
    pass


class GoogleGenAIEmbeddingsPublic(BaseGoogleGenAIEmbeddings):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class HuggingFaceEmbeddingsCreate(BaseHuggingFaceEmbeddings):
    pass


class HuggingFaceEmbeddingsUpdate(BaseHuggingFaceEmbeddings):
    pass


class HuggingFaceEmbeddingsPublic(BaseHuggingFaceEmbeddings):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


EmbeddingsCreate = GoogleGenAIEmbeddingsCreate | HuggingFaceEmbeddingsCreate
EmbeddingsUpdate = GoogleGenAIEmbeddingsUpdate | HuggingFaceEmbeddingsUpdate
EmbeddingsPublic = GoogleGenAIEmbeddingsPublic | HuggingFaceEmbeddingsPublic
