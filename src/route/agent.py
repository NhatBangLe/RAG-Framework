from typing import Annotated

from fastapi import APIRouter, status, Body

from ..data.dto.agent import AgentCreate, AgentUpdate, AgentPublic
from ..dependency import DownloadGeneratorDep, PagingQuery, AgentServiceDepend
from ..util import PagingWrapper

router = APIRouter(
    prefix="/api/v1/agent",
    tags=["Agent"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

AgentCreateBody = Annotated[AgentCreate, Body(
    examples=[{
        "name": "Another Example Agent",
        "description": "An example agent to illustrate required fields.",
        "language": "vi",
        "image_recognizer_id": "186003f271e4995bcb0c2d0f",
        "retriever_ids": ["686003f271e4995bcb0c2d0f"],
        "tool_ids": ["6886f26bc7b59ad39ab42e68"],
        "mcp_server_ids": ["6886f26bc7b59ad39ab42e68"],
        "llm_id": "686003f271e4995bcb0c2d0a",
        "prompt_id": "686003f271e4995bcb0c2e0f"
    }]
)]
AgentUpdateBody = Annotated[AgentUpdate, Body(
    examples=[{
        "name": "Updated Agent",
        "description": "An agent with updated information and additional tools.",
        "language": "en",
        "image_recognizer_id": "186003f271e4995bcb0c2d0f",
        "retriever_ids": [
            "686003f271e4995bcb0c2f0d",
            "f271e4995bcb0c2d0f686003"
        ],
        "tool_ids": [
            "a86003f271e4995bcb0c2d0f",
            "686003f271e4995bcb0c2d0e"
        ],
        "mcp_server_ids": ["6886f26bc7b59ad39ab42e68"],
        "llm_id": "686003f271e4995bcb0c2d0a",
        "prompt_id": "686003f271e4995bcb0c2e0f"
    }]
)]


@router.get(
    path="/{agent_id}/export",
    description="Export Agent configuration file. Get a token to download the file.",
    status_code=status.HTTP_200_OK)
async def export_config(agent_id: str, generator: DownloadGeneratorDep, service: AgentServiceDepend) -> str:
    return await service.get_exported_agent_config_file_token(agent_id, generator)


@router.get(
    path="/all",
    description="Get all agent configuration entities. Check chat model data response at corresponding endpoints.",
    response_model=PagingWrapper[AgentPublic],
    status_code=status.HTTP_200_OK)
async def get_all_models(params: PagingQuery, service: AgentServiceDepend):
    return await service.get_all_models_with_paging(params, True)


@router.get(
    path="/{agent_id}",
    response_model=AgentPublic,
    description="Get an agent configuration.",
    status_code=status.HTTP_200_OK)
async def get_agent_configuration(agent_id: str, service: AgentServiceDepend):
    return await service.get_model_by_id(agent_id)


@router.post(
    path="/create",
    description="Create an agent configuration. Returns an ID of the created agent configuration.",
    status_code=status.HTTP_201_CREATED)
async def create_agent_configuration(body: AgentCreateBody, service: AgentServiceDepend) -> str:
    return await service.create_new(body)


@router.put(
    path="/{model_id}/update",
    description="Update an agent configuration.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_agent_configuration(model_id: str, body: AgentUpdateBody, service: AgentServiceDepend) -> None:
    await service.update_model_by_id(model_id, body)


@router.delete(
    path="/{model_id}",
    description="Delete an agent configuration.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent_configuration(model_id: str, service: AgentServiceDepend) -> None:
    await service.delete_model_by_id(model_id)
