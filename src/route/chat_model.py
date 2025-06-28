from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter
from fastapi.params import Body
from starlette import status

from ..config.model.chat_model import LLMConfiguration
from ..data.database import get_collection, MongoCollection
from ..data.dto import GoogleGenAIChatModelPublic, GoogleGenAIChatModelCreate, OllamaChatModelCreate, \
    OllamaChatModelPublic
from ..data.model import GoogleGenAIChatModel, OllamaChatModel
from ..dependency import PagingQuery
from ..util import PagingWrapper
from ..util.error import NotFoundError

router = APIRouter(
    prefix="/api/v1/chat-model",
    tags=["Chat Model"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

GoogleGenAIChatModelCreateBody = Annotated[GoogleGenAIChatModelCreate, Body(
    example={
        "model_name": "gemini-2.0-flash",
        "temperature": 0.5,
        "max_tokens": 1024,
        "max_retries": 6,
        "timeout": None,
        "top_k": None,
        "top_p": None,
        "safety_settings": {
            "DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HATE_SPEECH": "BLOCK_ONLY_HIGH",
            "HARASSMENT": "BLOCK_LOW_AND_ABOVE",
            "SEXUALLY_EXPLICIT": "BLOCK_NONE"
        }
    }
)]
OllamaChatModelCreateBody = Annotated[OllamaChatModelCreate, Body(
    example={
        "model_name": "deepseek-r1",
        "base_url": "http://localhost:11434",
        "temperature": 0.8,
        "seed": None,
        "num_ctx": 2048,
        "num_predict": 128,
        "repeat_penalty": 1.1,
        "top_k": 40,
        "top_p": 0.9,
        "stop": ["</s>", "<|eot_id|>"]
    }
)]


async def get_model(model_id: str):
    collection = get_collection(MongoCollection.CHAT_MODEL)
    model = await collection.find_one({"_id": ObjectId(model_id)})
    if model is None:
        raise NotFoundError(f'No chat model with id {model_id} found.')
    return model


async def create_model(model: LLMConfiguration):
    collection = get_collection(MongoCollection.CHAT_MODEL)
    result = await collection.insert_one(model.model_dump())
    return str(result.inserted_id)


# Google GenAI
@router.get(
    path="/google-genai/{model_id}",
    response_model=GoogleGenAIChatModelPublic,
    description="Get a Google GenAI chat model.",
    status_code=status.HTTP_200_OK)
async def get_genai_model(model_id: str):
    return await get_model(model_id)


@router.post(
    path="/google-genai",
    description="Create a Google GenAI chat model.",
    status_code=status.HTTP_201_CREATED)
async def create_genai_model(data: GoogleGenAIChatModelCreateBody):
    model = GoogleGenAIChatModel.model_validate(data.model_dump())
    return await create_model(model)


# Ollama
@router.get(
    path="/ollama/{model_id}",
    response_model=OllamaChatModelPublic,
    description="Get an Ollama chat model.",
    status_code=status.HTTP_200_OK)
async def get_ollama_model(model_id: str):
    return await get_model(model_id)


@router.post(
    path="/ollama",
    description="Create an Ollama chat model.",
    status_code=status.HTTP_201_CREATED)
async def create_ollama_model(data: OllamaChatModelCreateBody):
    model = OllamaChatModel.model_validate(data.model_dump())
    return await create_model(model)


# Global
@router.get(
    path="/all",
    description="Get all chat models. Check chat model data response at corresponding endpoints.",
    status_code=status.HTTP_200_OK)
async def get_all_models(params: PagingQuery):
    collection = get_collection(MongoCollection.CHAT_MODEL)
    return await PagingWrapper.get_paging(params, collection)


@router.delete(
    path="/{model_id}",
    description="Delete a chat model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete(model_id: str):
    collection = get_collection(MongoCollection.CHAT_MODEL)
    await collection.delete_one({"_id": ObjectId(model_id)})
