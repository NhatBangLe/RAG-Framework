from typing import Annotated

from fastapi import APIRouter, status, Body

from ..data.dto.prompt import PromptPublic, PromptCreate, PromptUpdate
from ..data.function.prompt import get_prompt_as_document, get_all_prompts_as_documents, create_prompt_as_document, \
    update_prompt_as_document, delete_prompt_by_id
from ..dependency import PagingQuery
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
async def get_all_prompts(params: PagingQuery):
    return await get_all_prompts_as_documents(params)


@router.get(
    path="/{prompt_id}",
    response_model=PromptPublic,
    description="Get a prompt by its ID.",
    status_code=status.HTTP_200_OK)
async def get_prompt(prompt_id: str):
    return await get_prompt_as_document(prompt_id)


@router.post(
    path="/create",
    description="Create a prompt entity.",
    status_code=status.HTTP_201_CREATED)
async def create_prompt(data: PromptCreateBody):
    return await create_prompt_as_document(data)


@router.put(
    path="/{prompt_id}/update",
    description="Update a prompt entity.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_prompt(prompt_id: str, data: PromptUpdateBody):
    await update_prompt_as_document(prompt_id, data)


@router.delete(
    path="/{prompt_id}",
    description="Delete a prompt entity.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(prompt_id: str):
    await delete_prompt_by_id(prompt_id)
