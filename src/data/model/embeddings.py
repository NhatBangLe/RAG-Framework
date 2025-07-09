from pydantic import Field, ConfigDict

from .. import PyObjectId
from ..base_model.embeddings import BaseGoogleGenAIEmbeddings, BaseHuggingFaceEmbeddings


class GoogleGenAIEmbeddings(BaseGoogleGenAIEmbeddings):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class HuggingFaceEmbeddings(BaseHuggingFaceEmbeddings):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
