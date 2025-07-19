from enum import Enum

from pydantic import Field, BaseModel, field_validator

from ...config.model.embeddings.google_genai import GoogleGenAIEmbeddingsConfiguration
from ...config.model.embeddings.hugging_face import HuggingFaceEmbeddingsConfiguration


class EmbeddingsType(str, Enum):
    GOOGLE_GENAI = "google_genai"
    HUGGING_FACE = "hugging_face"


# noinspection PyNestedDecorators
class BaseEmbeddings(BaseModel):
    type: EmbeddingsType = Field(description="Type of the embeddings model.", frozen=True)
    name: str = Field(description="An unique name to determine embedding functions.")
    model_name: str = Field(min_length=1)

    @field_validator("name", mode="after")
    @classmethod
    def validate_name(cls, name: str):
        if len(name.strip()) == 0:
            raise ValueError(f'name cannot be blank.')
        return name


class BaseGoogleGenAIEmbeddings(BaseEmbeddings, GoogleGenAIEmbeddingsConfiguration):
    type: EmbeddingsType = EmbeddingsType.GOOGLE_GENAI


class BaseHuggingFaceEmbeddings(BaseEmbeddings, HuggingFaceEmbeddingsConfiguration):
    type: EmbeddingsType = EmbeddingsType.HUGGING_FACE
