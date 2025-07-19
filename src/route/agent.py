import datetime
import shutil
from pathlib import Path
from typing import Annotated

import jsonpickle
from fastapi import APIRouter, status, Body

from ..config.model.agent import AgentConfiguration
from ..data.base_model import BaseAgent
from ..data.database import get_collection, MongoCollection, get_by_id, update_by_id, create_document, delete_by_id
from ..data.dto.agent import AgentCreate, AgentUpdate, AgentPublic
from ..data.model import Agent
from ..dependency import DownloadGeneratorDep, PagingQuery
from ..util import SecureDownloadGenerator, FileInformation, PagingWrapper
from ..util.constant import DEFAULT_TIMEZONE
from ..util.error import NotFoundError
from ..util.function import zip_folder, get_cache_dir_path

router = APIRouter(
    prefix="/api/v1/agent",
    tags=["Agent"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

AgentCreateBody = Annotated[AgentCreate, Body(
    example={
        "name": "Another Example Agent",
        "description": "An example agent to illustrate required fields.",
        "language": "vi",
        "image_recognizer_id": "186003f271e4995bcb0c2d0f",
        "retriever_ids": ["686003f271e4995bcb0c2d0f"],
        "tool_ids": None,
        "mcp_id": None,
        "llm_id": "686003f271e4995bcb0c2d0a",
        "prompt_id": "686003f271e4995bcb0c2e0f"
    }
)]
AgentUpdateBody = Annotated[AgentUpdate, Body(
    example={
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
        "mcp_id": "686003f271e4995bcb0c2d0b",
        "llm_id": "686003f271e4995bcb0c2d0a",
        "prompt_id": "686003f271e4995bcb0c2e0f"
    }
)]


async def get_document(model_id: str):
    not_found_msg = f'No agent configuration with id {model_id} found.'
    return await get_by_id(model_id, MongoCollection.AGENT, not_found_msg)


async def update_document(model_id: str, model: BaseAgent):
    not_found_msg = f'Cannot update agent configuration with id {model_id}. Because no entity found.'
    await update_by_id(model_id, model, MongoCollection.AGENT, not_found_msg)


async def export_agent_config(agent_id: str, generator: SecureDownloadGenerator):
    collection = get_collection(MongoCollection.AGENT)
    doc_agent = await collection.find_one({"_id": agent_id})
    if doc_agent is None:
        raise NotFoundError(f"Agent with id {agent_id} not found.")
    agent = Agent.model_validate(doc_agent)

    # Prepare for exporting
    cache_dir = Path(get_cache_dir_path())
    current_datetime = datetime.datetime.now(DEFAULT_TIMEZONE)
    folder_for_exporting = cache_dir.joinpath(agent.id)
    file_ext = ".zip"
    exported_file = folder_for_exporting.with_name(f'{folder_for_exporting.name}{file_ext}')
    file_info: FileInformation = {
        "name": f'{folder_for_exporting.name}_{current_datetime.strftime("%d-%m-%Y_%H-%M-%S")}{file_ext}',
        "path": exported_file.absolute().resolve(),
        "mime_type": "application/zip"
    }
    cache_dir.mkdir(exist_ok=True)
    # Clear old folder and files
    if folder_for_exporting.is_dir():
        shutil.rmtree(str(folder_for_exporting.absolute().resolve()))
    if exported_file.is_file():
        exported_file.unlink(missing_ok=True)
    folder_for_exporting.mkdir()

    # Make the necessary directories
    config_dir = folder_for_exporting.joinpath("config")
    recognizer_dir = config_dir.joinpath("recognizer")
    retriever_dir = config_dir.joinpath("retriever")
    recognizer_dir.mkdir(parents=True)  # also make the parent config folder
    retriever_dir.mkdir()

    encoding = "utf-8"
    # Write a config.json file
    config_obj = AgentConfiguration.model_validate(agent)
    config_dir.joinpath("config.json").write_text(jsonpickle.encode(config_obj, indent=2), encoding=encoding)

    zip_folder(folder_for_exporting, exported_file)
    return generator.generate_token(file_info)


@router.get(
    path="/{agent_id}/export",
    description="Export Agent configuration file. Get a token to download the file.",
    status_code=status.HTTP_200_OK)
async def export_config(agent_id: str, generator: DownloadGeneratorDep) -> str:
    return await export_agent_config(agent_id, generator)


@router.get(
    path="/all",
    description="Get all agent configuration entities. Check chat model data response at corresponding endpoints.",
    response_model=PagingWrapper[AgentPublic],
    status_code=status.HTTP_200_OK)
async def get_all_models(params: PagingQuery):
    collection = get_collection(MongoCollection.AGENT)
    return await PagingWrapper.get_paging(params, collection)


@router.get(
    path="/{agent_id}",
    response_model=AgentPublic,
    description="Get an agent configuration.",
    status_code=status.HTTP_200_OK)
async def get_agent_configuration(agent_id: str):
    return await get_document(agent_id)


@router.post(
    path="/create",
    description="Create an agent configuration. Returns an ID of the created agent configuration.",
    status_code=status.HTTP_201_CREATED)
async def create_agent_configuration(body: AgentCreateBody) -> str:
    return await create_document(body, MongoCollection.AGENT)


@router.put(
    path="/{model_id}/update",
    description="Update an agent configuration.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_agent_configuration(model_id: str, body: AgentUpdateBody) -> None:
    await update_document(model_id, body)


@router.delete(
    path="/{model_id}",
    description="Delete an agent configuration.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent_configuration(model_id: str) -> None:
    await delete_by_id(model_id, MongoCollection.AGENT)
