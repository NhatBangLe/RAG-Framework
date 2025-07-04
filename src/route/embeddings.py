from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, status, Body

from ..config.model.embeddings import EmbeddingsConfiguration
from ..data.database import get_collection, MongoCollection, get_by_id, create_document, update_by_id
from ..data.dto.embeddings import GoogleGenAIEmbeddingsPublic, GoogleGenAIEmbeddingsCreate, GoogleGenAIEmbeddingsUpdate, \
    HuggingFaceEmbeddingsCreate, HuggingFaceEmbeddingsUpdate, HuggingFaceEmbeddingsPublic
from ..data.model.embeddings import GoogleGenAIEmbeddings, HuggingFaceEmbeddings
from ..dependency import PagingQuery
from ..util import PagingWrapper

router = APIRouter(
    prefix="/api/v1/embeddings",
    tags=["Embeddings"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

GoogleGenAIEmbeddingsCreateBody = Annotated[GoogleGenAIEmbeddingsCreate, Body(
    example={
        "name": "my_embedding_model",
        "model_name": "embedding-001",
        "task_type": "retrieval_query"
    }
)]
GoogleGenAIEmbeddingsUpdateBody = Annotated[GoogleGenAIEmbeddingsUpdate, Body(
    example={
        "name": "my_embedding_model",
        "model_name": "embedding-001",
        "task_type": "retrieval_query"
    }
)]
HuggingFaceEmbeddingsCreateBody = Annotated[HuggingFaceEmbeddingsCreate, Body(
    example={
        "name": "my_embedding_model",
        "model_name": "embedding-001"
    }
)]
HuggingFaceEmbeddingsUpdateBody = Annotated[HuggingFaceEmbeddingsUpdate, Body(
    example={
        "name": "my_embedding_model",
        "model_name": "embedding-001"
    }
)]


async def get_model(model_id: str):
    not_found_msg = f'No embeddings model with id {model_id} found.'
    return await get_by_id(model_id, MongoCollection.EMBEDDINGS, not_found_msg)


async def update_model(model_id: str, model: EmbeddingsConfiguration):
    not_found_msg = f'Cannot update embeddings model with id {model_id}. Because no embeddings model found.'
    await update_by_id(model_id, model, MongoCollection.EMBEDDINGS, not_found_msg)


@router.get(
    path="/google-genai/{model_id}",
    response_model=GoogleGenAIEmbeddingsPublic,
    description="Get a Google GenAI embeddings.",
    status_code=status.HTTP_200_OK)
async def get_genai_model(model_id: str):
    return await get_model(model_id)


@router.post(
    path="/google-genai",
    description="Create a Google GenAI embeddings.",
    status_code=status.HTTP_201_CREATED)
async def create_genai_model(data: GoogleGenAIEmbeddingsCreateBody):
    model = GoogleGenAIEmbeddings.model_validate(data.model_dump())
    return await create_document(model, MongoCollection.EMBEDDINGS)


@router.put(
    path="/google-genai/{model_id}",
    description="Update a Google GenAI embeddings model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_genai_model(model_id: str, data: GoogleGenAIEmbeddingsUpdateBody):
    model = GoogleGenAIEmbeddings.model_validate(data.model_dump())
    await update_model(model_id, model)


@router.get(
    path="/huggingface/{model_id}",
    response_model=HuggingFaceEmbeddingsPublic,
    description="Get a HuggingFace embeddings.",
    status_code=status.HTTP_200_OK)
async def get_huggingface_model(model_id: str):
    return await get_model(model_id)


@router.post(
    path="/huggingface",
    description="Create a HuggingFace embeddings.",
    status_code=status.HTTP_201_CREATED)
async def create_huggingface_model(data: HuggingFaceEmbeddingsCreateBody):
    model = HuggingFaceEmbeddings.model_validate(data.model_dump())
    return await create_document(model, MongoCollection.EMBEDDINGS)


@router.put(
    path="/huggingface/{model_id}",
    description="Update a HuggingFace embeddings model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_huggingface_model(model_id: str, data: HuggingFaceEmbeddingsUpdateBody):
    model = HuggingFaceEmbeddings.model_validate(data.model_dump())
    await update_model(model_id, model)


# Global
@router.get(
    path="/all",
    description="Get embeddings models. Check embeddings model data response at corresponding endpoints.",
    status_code=status.HTTP_200_OK)
async def get_all_models(params: PagingQuery):
    collection = get_collection(MongoCollection.EMBEDDINGS)
    return await PagingWrapper.get_paging(params, collection)


@router.delete(
    path="/{model_id}",
    description="Delete a embeddings model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete(model_id: str):
    collection = get_collection(MongoCollection.EMBEDDINGS)
    await collection.delete_one({"_id": ObjectId(model_id)})
