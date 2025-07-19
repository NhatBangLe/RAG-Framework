from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Body
from starlette import status

from ..data.base_model.chat_model import BaseChatModel, ChatModelType
from ..data.database import get_collection, MongoCollection, get_by_id, create_document, update_by_id, delete_by_id
from ..data.dto.chat_model import ChatModelCreate, ChatModelUpdate, \
    ChatModelPublic
from ..data.model.chat_model import GoogleGenAIChatModel, OllamaChatModel
from ..dependency import PagingQuery
from ..util import PagingWrapper
from ..util.error import InvalidArgumentError

router = APIRouter(
    prefix="/api/v1/chat-model",
    tags=["Chat Model"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

ChatModelCreateBody = Annotated[ChatModelCreate, Body(
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
ChatModelUpdateBody = Annotated[ChatModelUpdate, Body(
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


async def get_document(model_id: str):
    not_found_msg = f'No chat model with id {model_id} found.'
    return await get_by_id(model_id, MongoCollection.CHAT_MODEL, not_found_msg)


def get_model(base_data: BaseChatModel):
    if base_data.type == ChatModelType.GOOGLE_GENAI:
        return GoogleGenAIChatModel.model_validate(base_data.model_dump())
    elif base_data.type == ChatModelType.OLLAMA:
        return OllamaChatModel.model_validate(base_data.model_dump())
    else:
        raise InvalidArgumentError(f'Chat model type {base_data.type} is not supported.')


async def update_document(model_id: str, model: BaseChatModel):
    not_found_msg = f'Cannot update chat model with id {model_id}. Because no chat model found.'
    await update_by_id(model_id, model, MongoCollection.CHAT_MODEL, not_found_msg)


@router.get(
    path="/all",
    description="Get all chat models. Check chat model data response at corresponding endpoints.",
    response_model=PagingWrapper,
    status_code=status.HTTP_200_OK)
async def get_all_models(params: PagingQuery):
    collection = get_collection(MongoCollection.CHAT_MODEL)
    return await PagingWrapper.get_paging(params, collection)


@router.get(
    path="/{chat_model_id}",
    response_model=ChatModelPublic,
    description="Get a chat model.",
    status_code=status.HTTP_200_OK)
async def get_chat_model(chat_model_id: str):
    return await get_document(chat_model_id)


@router.post(
    path="/create",
    description="Create a chat model.",
    status_code=status.HTTP_201_CREATED)
async def create_chat_model(body: ChatModelCreateBody) -> str:
    return await create_document(get_model(body), MongoCollection.CHAT_MODEL)


@router.put(
    path="/{chat_model_id}/update",
    description="Update a chat model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_chat_model(chat_model_id: str, body: ChatModelUpdateBody) -> None:
    await update_document(chat_model_id, body)


@router.delete(
    path="/{chat_model_id}",
    description="Delete a chat model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_model(chat_model_id: str) -> None:
    await delete_by_id(chat_model_id, MongoCollection.CHAT_MODEL)
