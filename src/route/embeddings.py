from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, status, Body

from ..config.model.embeddings import EmbeddingsConfiguration
from ..data.database import get_collection, MongoCollection
from ..data.dto import GoogleGenAIEmbeddingsPublic, GoogleGenAIEmbeddingsCreate, GoogleGenAIEmbeddingsUpdate, \
    HuggingFaceEmbeddingsCreate, HuggingFaceEmbeddingsUpdate, HuggingFaceEmbeddingsPublic
from ..data.model import GoogleGenAIEmbeddings, HuggingFaceEmbeddings
from ..util.error import NotFoundError

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
    collection = get_collection(MongoCollection.EMBEDDINGS)
    model = await collection.find_one({"_id": ObjectId(model_id)})
    if model is None:
        raise NotFoundError(f'No embeddings model with id {model_id} found.')
    return model


async def create_model(data: EmbeddingsConfiguration):
    collection = get_collection(MongoCollection.EMBEDDINGS)
    created_model = await collection.insert_one(data.model_dump())
    return str(created_model.inserted_id)


async def update_model(model_id: str, model: EmbeddingsConfiguration):
    collection = get_collection(MongoCollection.CHAT_MODEL)
    query_filter = {'_id': ObjectId(model_id)}
    update_operation = {'$set': model.model_dump()}
    result = await collection.update_one(query_filter, update_operation)
    if result.modified_count == 0:
        raise NotFoundError(f'Cannot update embeddings model with id {model_id}. Because no embeddings model found.')


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
    return await create_model(model)


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
    return await create_model(model)


@router.put(
    path="/huggingface/{model_id}",
    description="Update a HuggingFace embeddings model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_huggingface_model(model_id: str, data: HuggingFaceEmbeddingsUpdateBody):
    model = HuggingFaceEmbeddings.model_validate(data.model_dump())
    await update_model(model_id, model)


@router.delete(
    path="/{model_id}",
    description="Delete a embeddings model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete(model_id: str):
    collection = get_collection(MongoCollection.EMBEDDINGS)
    await collection.delete_one({"_id": ObjectId(model_id)})
