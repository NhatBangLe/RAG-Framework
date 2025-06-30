from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Body
from starlette import status

from ..config.model.chat_model import LLMConfiguration
from ..data.database import get_collection, MongoCollection, get_by_id, create_document, update_by_id, delete_by_id
from ..data.dto import GoogleGenAIChatModelPublic, GoogleGenAIChatModelCreate, OllamaChatModelCreate, \
    OllamaChatModelPublic, GoogleGenAIChatModelUpdate, OllamaChatModelUpdate
from ..data.model import GoogleGenAIChatModel, OllamaChatModel
from ..dependency import PagingQuery
from ..util import PagingWrapper

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
        "timeout": 1.5,
        "top_k": 2,
        "top_p": 0.5,
        "safety_settings": {
            "DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HATE_SPEECH": "BLOCK_ONLY_HIGH",
            "HARASSMENT": "BLOCK_LOW_AND_ABOVE",
            "SEXUALLY_EXPLICIT": "BLOCK_NONE"
        }
    }
)]
GoogleGenAIChatModelUpdateBody = Annotated[GoogleGenAIChatModelUpdate, Body(
    example={
        "model_name": "gemini-2.0-flash",
        "temperature": 0.5,
        "max_tokens": 1024,
        "max_retries": 6,
        "timeout": 1.5,
        "top_k": 2,
        "top_p": 0.5,
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
OllamaChatModelUpdateBody = Annotated[OllamaChatModelUpdate, Body(
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
    not_found_msg = f'No chat model with id {model_id} found.'
    return await get_by_id(model_id, MongoCollection.CHAT_MODEL, not_found_msg)


async def update_model(model_id: str, model: LLMConfiguration):
    not_found_msg = f'Cannot update chat model with id {model_id}. Because no chat model found.'
    await update_by_id(model_id, model, MongoCollection.CHAT_MODEL, not_found_msg)


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
    return await create_document(model, MongoCollection.CHAT_MODEL)


@router.put(
    path="/google-genai/{model_id}",
    description="Update a Google GenAI chat model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_genai_model(model_id: str, data: GoogleGenAIChatModelUpdateBody):
    model = GoogleGenAIChatModel.model_validate(data.model_dump())
    await update_model(model_id, model)


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
    return await create_document(model, MongoCollection.CHAT_MODEL)


@router.put(
    path="/ollama/{model_id}",
    description="Update an Ollama chat model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_ollama_model(model_id: str, data: OllamaChatModelUpdateBody):
    model = OllamaChatModel.model_validate(data.model_dump())
    await update_model(model_id, model)


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
    await delete_by_id(model_id, MongoCollection.CHAT_MODEL)
