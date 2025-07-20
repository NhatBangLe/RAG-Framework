from typing import Annotated

from fastapi import APIRouter, status, Body

from ..data.dto.embeddings import EmbeddingsCreate, EmbeddingsUpdate, EmbeddingsPublic
from ..dependency import PagingQuery, EmbeddingsServiceDepend
from ..util import PagingWrapper

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


@router.get(
    path="/all",
    description="Get embeddings models. Check embeddings model data response at corresponding endpoints.",
    response_model=PagingWrapper,
    status_code=status.HTTP_200_OK)
async def get_all_embeddings_models(params: PagingQuery, service: EmbeddingsServiceDepend):
    return await service.get_all_models_with_paging(params)


@router.get(
    path="/{model_id}",
    response_model=EmbeddingsPublic,
    description="Get an embeddings model.",
    status_code=status.HTTP_200_OK)
async def get_embeddings_model(model_id: str, service: EmbeddingsServiceDepend):
    return await service.get_model_by_id(model_id)


@router.post(
    path="/create",
    description="Create an embeddings model. Returns an ID of the created embeddings model.",
    status_code=status.HTTP_201_CREATED)
async def create_embeddings_model(body: EmbeddingsCreateBody, service: EmbeddingsServiceDepend) -> str:
    return await service.create_new(body)


@router.put(
    path="/{model_id}/update",
    description="Update an embeddings model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_embeddings_model(model_id: str, body: EmbeddingsUpdateBody, service: EmbeddingsServiceDepend) -> None:
    await service.update_model_by_id(model_id, body)


@router.delete(
    path="/{model_id}",
    description="Delete an embeddings model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_embeddings_model(model_id: str, service: EmbeddingsServiceDepend) -> None:
    await service.delete_model_by_id(model_id)
