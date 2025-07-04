from pydantic import BaseModel, Field

from ...config.model.embeddings.google_genai import GoogleGenAIEmbeddingsTaskType


class BaseGoogleGenAIEmbeddings(BaseModel):
    name: str
    model_name: str = Field(min_length=1)
    task_type: GoogleGenAIEmbeddingsTaskType | None = Field(default=None)


class BaseHuggingFaceEmbeddings(BaseModel):
    name: str
    model_name: str = Field(min_length=1)
