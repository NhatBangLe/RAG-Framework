from typing import Annotated

from fastapi import APIRouter, status, Body

from ..data.base_model.embeddings import BaseEmbeddings, EmbeddingsType
from ..data.database import get_collection, MongoCollection, get_by_id, create_document, update_by_id, delete_by_id
from ..data.dto.embeddings import EmbeddingsCreate, EmbeddingsUpdate, EmbeddingsPublic
from ..data.model.embeddings import GoogleGenAIEmbeddings, HuggingFaceEmbeddings
from ..dependency import PagingQuery
from ..util import PagingWrapper
from ..util.error import InvalidArgumentError

router = APIRouter(
    prefix="/api/v1/embeddings",
    tags=["Embeddings"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

EmbeddingsCreateBody = Annotated[EmbeddingsCreate, Body(
    examples=[
        {
            "type": "google_genai",
            "name": "my_embedding_model",
            "model_name": "embedding-001",
            "task_type": "retrieval_query"
        },
        {
            "type": "hugging_face",
            "name": "my_embedding_model",
            "model_name": "embedding-001"
        }
    ]
)]
EmbeddingsUpdateBody = Annotated[EmbeddingsUpdate, Body(
    examples=[
        {
            "type": "google_genai",
            "name": "my_embedding_model",
            "model_name": "embedding-001",
            "task_type": "retrieval_query"
        },
        {
            "type": "hugging_face",
            "name": "my_embedding_model",
            "model_name": "embedding-001"
        }
    ]
)]


async def get_document(model_id: str):
    not_found_msg = f'No embeddings model with id {model_id} found.'
    return await get_by_id(model_id, MongoCollection.EMBEDDINGS, not_found_msg)


def get_model(base_data: BaseEmbeddings):
    if base_data.type == EmbeddingsType.GOOGLE_GENAI:
        return GoogleGenAIEmbeddings.model_validate(base_data.model_dump())
    elif base_data.type == EmbeddingsType.HUGGING_FACE:
        return HuggingFaceEmbeddings.model_validate(base_data.model_dump())
    else:
        raise InvalidArgumentError(f'Retriever type {base_data.type} is not supported.')


async def update_document(model_id: str, model: BaseEmbeddings):
    not_found_msg = f'Cannot update embeddings model with id {model_id}. Because no embeddings model found.'
    await update_by_id(model_id, model, MongoCollection.EMBEDDINGS, not_found_msg)


@router.get(
    path="/all",
    description="Get embeddings models. Check embeddings model data response at corresponding endpoints.",
    response_model=PagingWrapper,
    status_code=status.HTTP_200_OK)
async def get_all_embeddings_models(params: PagingQuery):
    collection = get_collection(MongoCollection.EMBEDDINGS)
    return await PagingWrapper.get_paging(params, collection)


@router.get(
    path="/{model_id}",
    response_model=EmbeddingsPublic,
    description="Get an embeddings model.",
    status_code=status.HTTP_200_OK)
async def get_embeddings_model(model_id: str):
    return await get_document(model_id)


@router.post(
    path="/create",
    description="Create an embeddings model. Returns an ID of the created embeddings model.",
    status_code=status.HTTP_201_CREATED)
async def create_embeddings_model(body: EmbeddingsCreateBody) -> str:
    return await create_document(get_model(body), MongoCollection.EMBEDDINGS)


@router.put(
    path="/{model_id}/update",
    description="Update an embeddings model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_embeddings_model(model_id: str, body: EmbeddingsUpdateBody) -> None:
    await update_document(model_id, body)


@router.delete(
    path="/{model_id}",
    description="Delete an embeddings model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_embeddings_model(model_id: str) -> None:
    await delete_by_id(model_id, MongoCollection.EMBEDDINGS)
