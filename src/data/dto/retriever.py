from pydantic import Field, ConfigDict

from .. import PyObjectId
from ..base_model.retriever import BaseBM25Retriever, BaseChromaRetriever


class BM25RetrieverCreate(BaseBM25Retriever):
    pass


class BM25RetrieverUpdate(BaseBM25Retriever):
    pass


class BM25RetrieverPublic(BaseBM25Retriever):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class ChromaRetrieverCreate(BaseChromaRetriever):
    pass


class ChromaRetrieverUpdate(BaseChromaRetriever):
    pass


class ChromaRetrieverPublic(BaseChromaRetriever):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


RetrieverCreate = BM25RetrieverCreate
RetrieverUpdate = BM25RetrieverUpdate
RetrieverPublic = BM25RetrieverPublic

VectorStoreCreate = ChromaRetrieverCreate
VectorStoreUpdate = ChromaRetrieverUpdate
VectorStorePublic = ChromaRetrieverPublic
