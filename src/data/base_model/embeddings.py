from enum import Enum

from pydantic import Field

from ...config.model.embeddings import EmbeddingsConfiguration
from ...config.model.embeddings.google_genai import GoogleGenAIEmbeddingsConfiguration
from ...config.model.embeddings.hugging_face import HuggingFaceEmbeddingsConfiguration


class EmbeddingsType(str, Enum):
    GOOGLE_GENAI = "google_genai"
    HUGGING_FACE = "hugging_face"


class BaseEmbeddings(EmbeddingsConfiguration):
    type: EmbeddingsType = Field(description="Type of the embeddings model.", frozen=True)


class BaseGoogleGenAIEmbeddings(BaseEmbeddings, GoogleGenAIEmbeddingsConfiguration):
    type: EmbeddingsType = EmbeddingsType.GOOGLE_GENAI


class BaseHuggingFaceEmbeddings(BaseEmbeddings, HuggingFaceEmbeddingsConfiguration):
    type: EmbeddingsType = EmbeddingsType.HUGGING_FACE
