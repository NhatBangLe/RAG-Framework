from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Body
from starlette import status

from ..data.dto.chat_model import ChatModelCreate, ChatModelUpdate, \
    ChatModelPublic
from ..dependency import PagingQuery, ChatModelServiceDepend
from ..util import PagingWrapper

router = APIRouter(
    prefix="/api/v1/chat-model",
    tags=["Chat Model"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

ChatModelCreateBody = Annotated[ChatModelCreate, Body(
    examples=[{
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
    }]
)]
ChatModelUpdateBody = Annotated[ChatModelUpdate, Body(
    examples=[{
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
    }]
)]


@router.get(
    path="/all",
    description="Get all chat models. Check chat model data response at corresponding endpoints.",
    response_model=PagingWrapper,
    status_code=status.HTTP_200_OK)
async def get_all_models(params: PagingQuery, service: ChatModelServiceDepend):
    return await service.get_all_models_with_paging(params, True)


@router.get(
    path="/{chat_model_id}",
    response_model=ChatModelPublic,
    description="Get a chat model.",
    status_code=status.HTTP_200_OK)
async def get_chat_model(chat_model_id: str, service: ChatModelServiceDepend):
    return await service.get_model_by_id(chat_model_id)


@router.post(
    path="/create",
    description="Create a chat model.",
    status_code=status.HTTP_201_CREATED)
async def create_chat_model(body: ChatModelCreateBody, service: ChatModelServiceDepend) -> str:
    return await service.create_new(body)


@router.put(
    path="/{chat_model_id}/update",
    description="Update a chat model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_chat_model(chat_model_id: str, body: ChatModelUpdateBody, service: ChatModelServiceDepend) -> None:
    await service.update_model_by_id(chat_model_id, body)


@router.delete(
    path="/{chat_model_id}",
    description="Delete a chat model.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_model(chat_model_id: str, service: ChatModelServiceDepend) -> None:
    await service.delete_model_by_id(chat_model_id)
