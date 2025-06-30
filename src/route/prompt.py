from typing import Annotated

from fastapi import APIRouter, status, Body

from src.data.database import MongoCollection, get_by_id, create_document, update_by_id, delete_by_id, get_collection
from src.data.dto import PromptPublic, PromptCreate, PromptUpdate
from src.data.model import Prompt
from src.dependency import PagingQuery
from src.util import PagingWrapper

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
    path="/{prompt_id}",
    response_model=PromptPublic,
    description="Get a prompt by its ID.",
    status_code=status.HTTP_200_OK)
async def get(prompt_id: str):
    return await get_by_id(prompt_id, MongoCollection.PROMPT)


@router.post(
    path="/create",
    description="Create a prompt entity.",
    status_code=status.HTTP_201_CREATED)
async def create(data: PromptCreateBody):
    model = Prompt.model_validate(data.model_dump())
    return await create_document(model, MongoCollection.PROMPT)


@router.put(
    path="/{prompt_id}/update",
    description="Update a prompt entity.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update(prompt_id: str, data: PromptUpdateBody):
    model = Prompt.model_validate(data.model_dump())
    await update_by_id(prompt_id, model, MongoCollection.PROMPT)


@router.get(
    path="/all",
    description="Get prompt entities. Check prompt entities data response at corresponding endpoints.",
    status_code=status.HTTP_200_OK)
async def get_all_prompts(params: PagingQuery):
    collection = get_collection(MongoCollection.PROMPT)
    return await PagingWrapper.get_paging(params, collection)


@router.delete(
    path="/{prompt_id}",
    description="Delete a prompt entity.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete(prompt_id: str):
    await delete_by_id(prompt_id, MongoCollection.PROMPT)
