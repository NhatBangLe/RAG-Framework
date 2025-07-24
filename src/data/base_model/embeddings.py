from ...config.model.embeddings import EmbeddingsConfiguration
from ...config.model.embeddings.google_genai import GoogleGenAIEmbeddingsConfiguration
from ...config.model.embeddings.hugging_face import HuggingFaceEmbeddingsConfiguration


class BaseEmbeddings(EmbeddingsConfiguration):
    pass


class BaseGoogleGenAIEmbeddings(BaseEmbeddings, GoogleGenAIEmbeddingsConfiguration):
    pass


class BaseHuggingFaceEmbeddings(BaseEmbeddings, HuggingFaceEmbeddingsConfiguration):
    pass
