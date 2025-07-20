from typing import Annotated

from fastapi import APIRouter, status, Body

from ..data.dto.prompt import PromptPublic, PromptCreate, PromptUpdate
from ..dependency import PagingQuery, PromptServiceDepend
from ..util import PagingWrapper

router = APIRouter(
    prefix="/api/v1/prompt",
    tags=["Prompt"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

PromptCreateBody = Annotated[PromptCreate, Body(
    example={
        "suggest_questions_prompt": "You are an expert at generating questions on various subjects.",
        "respond_prompt": "You are a Question-Answering assistant."
                          "You are an AI Agent that built by using LangGraph and LLMs."
                          "\nYour mission is that you need to analyze and answer questions."
                          "\nAnswer by the language which is related to the questions."
                          "\nYou can use accessible tools to retrieve more information if you want."
    }
)]
PromptUpdateBody = Annotated[PromptUpdate, Body(
    example={
        "suggest_questions_prompt": "You are an expert at generating questions on various subjects.",
        "respond_prompt": "You are a Question-Answering assistant."
                          "You are an AI Agent that built by using LangGraph and LLMs."
                          "\nYour mission is that you need to analyze and answer questions."
                          "\nAnswer by the language which is related to the questions."
                          "\nYou can use accessible tools to retrieve more information if you want."
    }
)]


@router.get(
    path="/all",
    description="Get prompt entities. Check prompt entities data response at corresponding endpoints.",
    response_model=PagingWrapper[PromptPublic],
    status_code=status.HTTP_200_OK)
async def get_all_prompts(params: PagingQuery, service: PromptServiceDepend):
    return await service.get_all_models_with_paging(params)


@router.get(
    path="/{prompt_id}",
    response_model=PromptPublic,
    description="Get a prompt by its ID.",
    status_code=status.HTTP_200_OK)
async def get_prompt(prompt_id: str, service: PromptServiceDepend):
    return await service.get_model_by_id(prompt_id)


@router.post(
    path="/create",
    description="Create a prompt entity.",
    status_code=status.HTTP_201_CREATED)
async def create_prompt(data: PromptCreateBody, service: PromptServiceDepend):
    return await service.create_new(data)


@router.put(
    path="/{prompt_id}/update",
    description="Update a prompt entity.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_prompt(prompt_id: str, data: PromptUpdateBody, service: PromptServiceDepend):
    await service.update_model_by_id(prompt_id, data)


@router.delete(
    path="/{prompt_id}",
    description="Delete a prompt entity.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(prompt_id: str, service: PromptServiceDepend):
    await service.delete_model_by_id(prompt_id)
