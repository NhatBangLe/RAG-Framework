from pydantic import Field, ConfigDict

from ..base_model.retriever import BaseChromaRetriever
from .. import PyObjectId
from ..base_model.retriever import BaseBM25Retriever


class BM25Retriever(BaseBM25Retriever):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class ChromaRetriever(BaseChromaRetriever):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


Retriever = BM25Retriever | ChromaRetriever
