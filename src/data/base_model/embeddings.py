from pydantic import Field

from ...config.model.embeddings import EmbeddingsConfiguration
from ...config.model.embeddings.google_genai import GoogleGenAIEmbeddingsTaskType


class BaseGoogleGenAIEmbeddings(EmbeddingsConfiguration):
    task_type: GoogleGenAIEmbeddingsTaskType | None = Field(default=None)


class BaseHuggingFaceEmbeddings(EmbeddingsConfiguration):
    pass
