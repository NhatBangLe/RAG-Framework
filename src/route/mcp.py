from typing import Annotated

from fastapi import APIRouter, status, Body

from ..data.dto.mcp import MCPCreate, MCPUpdate, MCPPublic
from ..dependency import PagingQuery, MCPServiceDepend
from ..util import PagingWrapper

router = APIRouter(
    prefix="/api/v1/mcp",
    tags=["MCP"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

MCPCreateBody = Annotated[MCPCreate, Body(
    example={
        "servers": [
            {
                "name": "example_streamable_server",
                "type": "streamable_http",
                "url": "https://api.example.com/stream",
                "headers": {
                    "Authorization": "Bearer your_token_here",
                    "Content-Type": "application/json"
                },
                "timeout": 60,
                "sse_read_timeout": 300,
                "terminate_on_close": True
            },
            {
                "name": "another_streamable_server",
                "transport": "streamable_http",
                "type": "streamable_http",
                "url": "https://another.example.com/data",
                "timeout": 90
            }
        ]
    }
)]
MCPUpdateBody = Annotated[MCPUpdate, Body(
    example={
        "servers": [
            {
                "name": "a_streamable_server",
                "transport": "streamable_http",
                "type": "streamable_http",
                "url": "https://api.example.com/stream",
                "timeout": 60,
                "sse_read_timeout": 300,
                "terminate_on_close": True
            },
            {
                "name": "another_streamable_server",
                "transport": "streamable_http",
                "type": "streamable_http",
                "url": "https://another.example.com/data",
                "timeout": 90
            }
        ]
    }
)]


@router.get(
    path="/all",
    description="Get MCP entities.",
    response_model=PagingWrapper[MCPPublic],
    status_code=status.HTTP_200_OK)
async def get_all_mcp_configs(params: PagingQuery, service: MCPServiceDepend):
    return await service.get_all_models_with_paging(params)


@router.get(
    path="/{model_id}",
    response_model=MCPPublic,
    description="Get a MCP configuration.",
    status_code=status.HTTP_200_OK)
async def get_mcp_configuration(model_id: str, service: MCPServiceDepend):
    return await service.get_model_by_id(model_id)


@router.post(
    path="/create",
    description="Create a MCP configuration. Returns an ID of the created MCP configuration.",
    status_code=status.HTTP_201_CREATED)
async def create_mcp_configuration(body: MCPCreateBody, service: MCPServiceDepend) -> str:
    return await service.create_new(body)


@router.put(
    path="/{model_id}/update",
    description="Update a MCP configuration.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_mcp_configuration(model_id: str, body: MCPUpdateBody, service: MCPServiceDepend) -> None:
    await service.update_model_by_id(model_id, body)


@router.delete(
    path="/{model_id}",
    description="Delete a MCP configuration.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp_configuration(model_id: str, service: MCPServiceDepend) -> None:
    await service.delete_model_by_id(model_id)
