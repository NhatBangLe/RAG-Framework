from enum import Enum

from pydantic import Field, field_validator, BaseModel

from ...config.model.retriever.vector_store import VectorStoreConfigurationMode, VectorStoreConnection


class RetrieverType(str, Enum):
    BM25 = "bm25"
    CHROMA_DB = "chroma_db"


# noinspection PyNestedDecorators
class BaseRetriever(BaseModel):
    type: RetrieverType = Field(description="Type of the retriever.", frozen=True)
    name: str = Field(description="An unique name is used for determining retrievers.", min_length=1, max_length=100)
    weight: float = Field(description="Retriever weight for combining results", ge=0.0, le=1.0)
    k: int = Field(default=4, description="Amount of documents to return")

    @field_validator("name", mode="after")
    @classmethod
    def validate_name(cls, name: str):
        if len(name.strip()) == 0:
            raise ValueError(f'name cannot be blank.')
        return name


class BaseBM25Retriever(BaseRetriever):
    type: RetrieverType = RetrieverType.BM25
    embeddings_id: str = Field(description="ID of the configured embeddings model.")
    removal_words_file_id: str | None = Field(default=None,
                                              description="ID of a word-file which provides removal words.")
    enable_remove_emoji: bool = Field(default=False)
    enable_remove_emoticon: bool = Field(default=False)


class BaseVectorStoreRetriever(BaseRetriever):
    mode: VectorStoreConfigurationMode = Field(default="persistent")
    embeddings_id: str = Field(description="ID of the configured embeddings model.")
    connection: VectorStoreConnection | None = Field(
        default=None, description="Connection will be used if the mode value is remote")
    collection_name: str = Field(default="agent_collection",
                                 description="Name of the collection in vector store.")


class BaseChromaRetriever(BaseVectorStoreRetriever):
    type: RetrieverType = RetrieverType.CHROMA_DB
    tenant: str = Field(default="default_tenant", min_length=1)
    database: str = Field(default="default_database", min_length=1)
