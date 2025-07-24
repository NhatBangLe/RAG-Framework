from typing import Annotated

from fastapi import APIRouter, status, Body

from ..data.base_model.retriever import RetrieverType
from ..data.dto.retriever import RetrieverCreate, RetrieverUpdate, VectorStorePublic, VectorStoreCreate, \
    VectorStoreUpdate, RetrieverPublic
from ..dependency import PagingQuery, RetrieverServiceDepend
from ..util import PagingWrapper

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
            "removal_words_file_id": "686003f271e4995bcb0c2d0f"
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
        }
    ]
)]

VectorStoreCreateBody = Annotated[VectorStoreCreate, Body(
    examples=[
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
            "tenant": "default_tenant",
            "database": "default_database"
        }
    ]
)]
VectorStoreUpdateBody = Annotated[VectorStoreUpdate, Body(
    examples=[
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
            "tenant": "default_tenant",
            "database": "default_database"
        }
    ]
)]


@router.get(
    path="/vector-store/all",
    response_model=PagingWrapper[VectorStorePublic],
    description="Get all vector stores.",
    status_code=status.HTTP_200_OK)
async def get_all_vector_stores(params: PagingQuery, service: RetrieverServiceDepend):
    data = await service.get_all_models_with_paging(params, True)
    content = list(filter(lambda x: x.type == RetrieverType.CHROMA_DB, data.content))
    return PagingWrapper(
        content=content,
        first=data.first,
        last=data.last,
        total_elements=data.total_elements,
        total_pages=data.total_pages,
        page_number=data.page_number,
        page_size=data.page_size,
    )


@router.get(
    path="/vector-store/{store_id}",
    response_model=VectorStorePublic,
    description="Get a vector store by its ID.",
    status_code=status.HTTP_200_OK)
async def get_vector_store(store_id: str, service: RetrieverServiceDepend):
    return await service.get_model_by_id(store_id)


@router.post(
    path="/vector-store/create",
    description="Create a vector store. Returns an ID of the created vector store.",
    status_code=status.HTTP_200_OK)
async def create_vector_store(body: RetrieverCreateBody, service: RetrieverServiceDepend) -> str:
    return await service.create_new(body)


@router.put(
    path="/vector-store/{store_id}/update",
    description="Update a vector store.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_vector_store(store_id: str, body: RetrieverUpdateBody, service: RetrieverServiceDepend) -> None:
    await service.update_model_by_id(store_id, body)


@router.get(
    path="/bm25/all",
    response_model=PagingWrapper[RetrieverPublic],
    description="Get all BM25 configs.",
    status_code=status.HTTP_200_OK)
async def get_all_bm25_configs(params: PagingQuery, service: RetrieverServiceDepend):
    data = await service.get_all_models_with_paging(params, True)
    content = list(filter(lambda x: x.type == RetrieverType.BM25, data.content))
    return PagingWrapper(
        content=content,
        first=data.first,
        last=data.last,
        total_elements=data.total_elements,
        total_pages=data.total_pages,
        page_number=data.page_number,
        page_size=data.page_size,
    )


@router.get(
    path="/bm25/{retriever_id}",
    response_model=RetrieverPublic,
    description="Get a retriever by its ID.",
    status_code=status.HTTP_200_OK)
async def get_retriever(retriever_id: str, service: RetrieverServiceDepend):
    return await service.get_model_by_id(retriever_id)


@router.post(
    path="/bm25/create",
    description="Create a retriever. Returns an ID of the created retriever.",
    status_code=status.HTTP_200_OK)
async def create_retriever(body: RetrieverCreateBody, service: RetrieverServiceDepend) -> str:
    return await service.create_new(body)


@router.put(
    path="/bm25/{retriever_id}/update",
    description="Update a retriever.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_retriever(retriever_id: str, body: RetrieverUpdateBody, service: RetrieverServiceDepend) -> None:
    await service.update_model_by_id(retriever_id, body)


@router.delete(
    path="/{retriever_id}",
    description="Delete a retriever.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_retriever(retriever_id: str, service: RetrieverServiceDepend) -> None:
    await service.delete_model_by_id(retriever_id)
