from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Body

from ..data.dto.tool import ToolCreate, ToolUpdate, ToolPublic
from ..dependency import PagingQuery, ToolServiceDepend
from ..util import PagingWrapper

router = APIRouter(
    prefix="/api/v1/tool",
    tags=["Tool"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

ToolCreateBody = Annotated[ToolCreate, Body(
    examples=[
        {
            "name": "duckduckgo_search",
            "type": "duckduckgo_search",
            "max_results": 4
        }
    ]
)]
ToolUpdateBody = Annotated[ToolUpdate, Body(
    examples=[
        {
            "name": "duckduckgo_search",
            "type": "duckduckgo_search",
            "max_results": 4
        }
    ]
)]


@router.get(
    path="/all",
    description="Get all tools. Check chat model data response at corresponding endpoints.",
    response_model=PagingWrapper,
    status_code=status.HTTP_200_OK)
async def get_all_tools(params: PagingQuery, service: ToolServiceDepend):
    return await service.get_all_models_with_paging(params, True)


@router.get(
    path="/{tool_id}",
    response_model=ToolPublic,
    description="Get a tool.",
    status_code=status.HTTP_200_OK)
async def get_tool(tool_id: str, service: ToolServiceDepend):
    return await service.get_model_by_id(tool_id)


@router.post(
    path="/create",
    description="Create a tool.",
    status_code=status.HTTP_201_CREATED)
async def create_tool(body: ToolCreateBody, service: ToolServiceDepend) -> str:
    return await service.create_new(body)


@router.put(
    path="/{tool_id}/update",
    description="Update a tool.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_tool(tool_id: str, body: ToolUpdateBody, service: ToolServiceDepend) -> None:
    await service.update_model_by_id(tool_id, body)


@router.delete(
    path="/{tool_id}",
    description="Delete a tool.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(tool_id: str, service: ToolServiceDepend) -> None:
    await service.delete_model_by_id(tool_id)
