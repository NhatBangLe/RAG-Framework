from typing import Annotated

from fastapi import APIRouter, status, Body

from ..data.dto.mcp import MCPCreate, MCPUpdate, MCPPublic
from ..data.function.mcp import get_mcp_as_document, update_mcp_as_document, delete_mcp_by_id, \
    get_all_mcp_entities_as_documents, create_mcp_as_document
from ..dependency import PagingQuery
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
async def get_all_mcp_configs(params: PagingQuery):
    return await get_all_mcp_entities_as_documents(params)


@router.get(
    path="/{model_id}",
    response_model=MCPPublic,
    description="Get a MCP configuration.",
    status_code=status.HTTP_200_OK)
async def get_mcp_configuration(model_id: str):
    return await get_mcp_as_document(model_id)


@router.post(
    path="/create",
    description="Create a MCP configuration. Returns an ID of the created MCP configuration.",
    status_code=status.HTTP_201_CREATED)
async def create_mcp_configuration(body: MCPCreateBody) -> str:
    return await create_mcp_as_document(body)


@router.put(
    path="/{model_id}/update",
    description="Update a MCP configuration.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_mcp_configuration(model_id: str, body: MCPUpdateBody) -> None:
    await update_mcp_as_document(model_id, body)


@router.delete(
    path="/{model_id}",
    description="Delete a MCP configuration.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp_configuration(model_id: str) -> None:
    await delete_mcp_by_id(model_id)
