from typing import Annotated

from fastapi import APIRouter, status, Body

from ..data.base_model.retriever import BaseRetriever, RetrieverType
from ..data.database import get_collection, MongoCollection, update_by_id, get_by_id, delete_by_id, create_document
from ..data.dto.retriever import RetrieverCreate, RetrieverUpdate, RetrieverPublic
from ..data.model.retriever import BM25Retriever, ChromaRetriever
from ..dependency import PagingQuery
from ..util import PagingWrapper
from ..util.error import InvalidArgumentError


async def get_document(retriever_id: str):
    not_found_msg = f'No retriever with id {retriever_id} found.'
    return await get_by_id(retriever_id, MongoCollection.RETRIEVER, not_found_msg)


def get_model(base_retriever: BaseRetriever):
    if base_retriever.type == RetrieverType.BM25:
        return BM25Retriever.model_validate(base_retriever.model_dump())
    elif base_retriever.type == RetrieverType.CHROMA_DB:
        return ChromaRetriever.model_validate(base_retriever.model_dump())
    else:
        raise InvalidArgumentError(f'Retriever type {base_retriever.type} is not supported.')


async def update_document(retriever_id: str, data: BaseRetriever):
    not_found_msg = f'Cannot update retriever with id {retriever_id}. Because no retriever found.'
    await update_by_id(retriever_id, data, MongoCollection.RETRIEVER, not_found_msg)


router = APIRouter(
    prefix="/api/v1/retriever",
    tags=["Retriever"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

RetrieverCreateBody = Annotated[RetrieverCreate, Body(
    examples=[
        {
            "type": "bm25",
            "weight": 0.5,
            "name": "default_bm25_retriever",
            "embeddings_id": "686003f271e4995bcb0c2d0f",
            "k": 4,
            "enable_remove_emoji": False,
            "enable_remove_remove_emoticon": False,
            "removal_words_file_id": None
        },
        {
            "type": "chroma_db",
            "name": "default_chroma_retriever",
            "weight": 1.0,
            "mode": "persistent",
            "persist_directory": "chroma_persist",
            "collection_name": "chroma_collection",
            "external_data_file_id": None,
            "connection": None,
            "embeddings_id": "some_embedding_model_id",
            "k": 4,
            "tenant": "default",
            "database": "default"
        }
    ]
)]
RetrieverUpdateBody = Annotated[RetrieverUpdate, Body(
    examples=[
        {
            "type": "bm25",
            "weight": 0.5,
            "name": "default_bm25_retriever",
            "embeddings_id": "686003f271e4995bcb0c2d0f",
            "k": 4,
            "enable_remove_emoji": False,
            "enable_remove_remove_emoticon": False,
            "removal_words_file_id": None
        },
        {
            "type": "chroma_db",
            "name": "default_chroma_retriever",
            "weight": 1.0,
            "mode": "persistent",
            "persist_directory": "chroma_persist",
            "collection_name": "chroma_collection",
            "external_data_file_id": None,
            "connection": None,
            "embeddings_id": "some_embedding_model_id",
            "k": 4,
            "tenant": "default",
            "database": "default"
        }
    ]
)]


@router.get(
    path="/all",
    response_model=PagingWrapper,
    description="Get all retrievers.",
    status_code=status.HTTP_200_OK)
async def get_all(params: PagingQuery):
    collection = get_collection(MongoCollection.RETRIEVER)
    return await PagingWrapper.get_paging(params, collection)


@router.get(
    path="/{retriever_id}",
    response_model=RetrieverPublic,
    description="Get a retriever by its ID.",
    status_code=status.HTTP_200_OK)
async def get_retriever(retriever_id: str):
    return await get_document(retriever_id)


@router.post(
    path="/create",
    description="Create a retriever. Returns an ID of the created retriever.",
    status_code=status.HTTP_200_OK)
async def create_retriever(body: RetrieverCreateBody) -> str:
    return await create_document(get_model(body), MongoCollection.RETRIEVER)


@router.put(
    path="/{retriever_id}/update",
    description="Update a retriever.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_retriever(retriever_id: str, body: RetrieverUpdateBody) -> None:
    await update_document(retriever_id, body)


@router.delete(
    path="/{retriever_id}",
    description="Delete a retriever.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_retriever(retriever_id: str) -> None:
    await delete_by_id(retriever_id, MongoCollection.RETRIEVER)
