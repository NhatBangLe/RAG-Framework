from pydantic import Field, BaseModel

from ...config.model.embeddings import EmbeddingsType
from ...config.model.embeddings.google_genai import GoogleGenAIEmbeddingsConfiguration
from ...config.model.embeddings.hugging_face import HuggingFaceEmbeddingsConfiguration


class BaseEmbeddings(BaseModel):
    name: str = Field(description="An unique name to determine embedding functions.")
    model_name: str = Field(min_length=1)
    type: EmbeddingsType = Field(description="The type of embedding model to use.")


class BaseGoogleGenAIEmbeddings(BaseEmbeddings, GoogleGenAIEmbeddingsConfiguration):
    type: EmbeddingsType = Field(default=EmbeddingsType.GOOGLE_GENAI, frozen=True)


class BaseHuggingFaceEmbeddings(BaseEmbeddings, HuggingFaceEmbeddingsConfiguration):
    type: EmbeddingsType = Field(default=EmbeddingsType.HUGGING_FACE, frozen=True)
