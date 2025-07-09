from enum import Enum

from pydantic import Field

from ...config.model.retriever import RetrieverConfiguration
from ...config.model.retriever.bm25 import BM25Configuration
from ...config.model.retriever.vector_store.chroma import ChromaVSConfiguration


class RetrieverType(str, Enum):
    BM25 = "bm25"
    CHROMA_DB = "chroma_db"


class BaseRetriever(RetrieverConfiguration):
    type: RetrieverType = Field(description="Type of the retriever.", frozen=True)


class BaseBM25Retriever(BaseRetriever, BM25Configuration):
    type: RetrieverType = RetrieverType.BM25
    embeddings_id: str = Field(description="ID of the configured embeddings model.")
    removal_words_file_id: str | None = Field(default=None,
                                              description="ID of a word-file which provides removal words.")
    # Exclude fields
    embeddings_model: str | None = Field(default=None, exclude=True)
    removal_words_path: str | None = Field(default=None, exclude=True)


class BaseChromaRetriever(BaseRetriever, ChromaVSConfiguration):
    type: RetrieverType = RetrieverType.CHROMA_DB
    external_data_file_id: str | None = Field(default=None,
                                              description="ID of a file which provides external data.")
    embeddings_id: str = Field(description="ID of the configured embeddings model.")

    # Exclude fields
    embeddings_model: str | None = Field(default=None, exclude=True)
    external_data_config_path: str | None = Field(default=None, exclude=True)
