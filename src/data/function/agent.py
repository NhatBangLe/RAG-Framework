import asyncio
import logging
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Literal

import jsonpickle

from src.config.model.agent import AgentConfiguration
from .chat_model import IChatModelService
from .embeddings import IEmbeddingsService
from .mcp import IMCPService
from .prompt import IPromptService
from .recognizer import IRecognizerService
from .retriever import IRetrieverService
from ..base_model import BaseMCPServer
from ..database import get_by_id, MongoCollection, update_by_id, create_document, delete_by_id, get_collection
from ..dto.agent import AgentUpdate, AgentCreate, AgentPublic
from ..model import Agent
from ...config.model.mcp import MCPConnectionConfiguration, MCPConfiguration
from ...config.model.retriever import RetrieverConfiguration
from ...config.model.retriever.bm25 import BM25Configuration
from ...config.model.retriever.vector_store import VectorStoreConfiguration
from ...util import SecureDownloadGenerator, FileInformation, PagingParams, PagingWrapper, DEFAULT_CHARSET
from ...util.constant import AgentEnvVar
from ...util.error import NotFoundError
from ...util.function import get_cache_dir_path, get_datetime_now, zip_folder, strict_bson_id_parser


class IAgentService(ABC):

    @staticmethod
    @abstractmethod
    def get_export_path(agent_id: str, level: Literal["root", "config", "recognizer", "retriever"]) -> Path:
        """
        Determines and creates the appropriate export directory path for an agent.

        Args:
            agent_id: The ID of the agent.
            level: The specific subdirectory level to retrieve ("root", "config", "recognizer", "retriever").

        Returns:
            A Path object representing the export directory.

        Raises:
            ValueError: If an invalid level is provided.
        """
        pass

    @abstractmethod
    async def get_all_models_with_paging(self, params: PagingParams,
                                         to_public: bool) -> PagingWrapper[Agent | AgentPublic]:
        """
        Retrieves all agent configurations with pagination.

        Args:
            params: Pagination parameters.
            to_public: Whether to return public agent data or not.

        Returns:
            A PagingWrapper containing a list of Agent objects.
        """
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_model(data: dict[str, Any]) -> Agent:
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_public(data: dict[str, Any]) -> AgentPublic:
        pass

    @abstractmethod
    async def get_model_by_id(self, model_id: str) -> Agent:  # Assuming it returns Agent after validation
        """
        Retrieves an agent configuration document by its ID.

        Args:
            model_id: The unique identifier of the agent configuration.

        Returns:
            An Agent object representing the configuration.

        Raises:
            NotFoundError: If no agent configuration with the given ID is found.
        """
        pass

    @abstractmethod
    async def create_new(self, data: AgentCreate) -> str:
        """
        Creates a new agent configuration.

        Args:
            data: The data for creating the new agent.

        Returns:
            The ID of the newly created agent document.
        """
        pass

    @abstractmethod
    async def update_model_by_id(self, model_id: str, data: AgentUpdate) -> None:
        """
        Updates an existing agent configuration by its ID.

        Args:
            model_id: The unique identifier of the agent to update.
            data: The updated data for the agent.

        Raises:
            NotFoundError: If no agent with the given ID is found.
        """
        pass

    @abstractmethod
    async def delete_model_by_id(self, model_id: str) -> None:
        """
        Deletes an agent configuration by its ID.

        Args:
            model_id: The unique identifier of the agent to delete.

        Raises:
            NotFoundError: If no agent with the given ID is found.
            IOError: If there's an issue deleting associated cache files.
        """
        pass

    @abstractmethod
    async def get_exported_agent_config_file_token(self, agent_id: str, generator: SecureDownloadGenerator) -> str:
        """
        Generates a downloadable token for an agent's complete configuration,
        including associated files, packaged as a zip archive.

        Args:
            agent_id: The ID of the agent to export.
            generator: An instance of SecureDownloadGenerator to create the download token.

        Returns:
            A secure token for downloading the agent's configuration file.

        Raises:
            NotFoundError: If no agent with the given ID is found.
            IOError: If there's an issue with file system operations (e.g., writing, zipping).
        """
        pass


def _write_env_file(folder_for_exporting: Path, agent: AgentConfiguration):
    env_file = folder_for_exporting.joinpath(".env")
    env_set: set[str] = set()

    for v in AgentEnvVar:
        env_set.add(v.value)
    env_set.add(agent.llm.get_api_key_env())
    if agent.retriever is not None:
        for retriever in agent.retrievers:
            if isinstance(retriever, VectorStoreConfiguration):
                env_set.add(retriever.embeddings_model.get_api_key_env())
            elif isinstance(retriever, BM25Configuration):
                env_set.add(retriever.embeddings_model.get_api_key_env())
    if agent.tools is not None:
        for tool in agent.tools:
            env_set.add(tool.get_api_key_env())

    env_file.write_text("=\n".join(filter(lambda value: value is not None, env_set)), encoding=DEFAULT_CHARSET)


class AgentServiceImpl(IAgentService):
    _logger = logging.getLogger(__name__)

    def __init__(self,
                 chat_model_service: IChatModelService,
                 mcp_service: IMCPService,
                 recognizer_service: IRecognizerService,
                 prompt_service: IPromptService,
                 embeddings_service: IEmbeddingsService,
                 retriever_service: IRetrieverService):
        self._chat_model_service = chat_model_service
        self._mcp_service = mcp_service
        self._recognizer_service = recognizer_service
        self._prompt_service = prompt_service
        self._embeddings_service = embeddings_service
        self._retriever_service = retriever_service
        self._collection_name = MongoCollection.AGENT

    @staticmethod
    def get_export_path(agent_id, level):
        cache_dir = Path(get_cache_dir_path())
        cache_dir.mkdir(exist_ok=True)

        root_dir = Path(cache_dir, agent_id)
        if level == "root":
            root_dir.mkdir(parents=True, exist_ok=True)
            return root_dir
        elif level == "config":
            config_dir = root_dir.joinpath("config")
            config_dir.mkdir(parents=True, exist_ok=True)
            return config_dir
        elif level == "recognizer":
            recognizer_dir = root_dir.joinpath("config", "recognizer")
            recognizer_dir.mkdir(parents=True, exist_ok=True)
            return recognizer_dir
        elif level == "retriever":
            retriever_dir = root_dir.joinpath("config", "retriever")
            retriever_dir.mkdir(parents=True, exist_ok=True)
            return retriever_dir
        else:
            raise ValueError(f"Invalid level: {level}")

    async def get_all_models_with_paging(self, params, to_public):
        collection = get_collection(self._collection_name)
        map_func = self.convert_dict_to_public if to_public else self.convert_dict_to_model
        return await PagingWrapper.get_paging(params, collection, map_func)

    async def get_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'No agent configuration with id {model_id} found.'
        return await get_by_id(valid_id, self._collection_name, not_found_msg)

    @staticmethod
    def convert_dict_to_model(data):
        return Agent.model_validate(data)

    @staticmethod
    def convert_dict_to_public(data):
        return AgentPublic.model_validate(data)

    async def create_new(self, data):
        model = Agent.model_validate(data.model_dump())
        await self._check_entities_exists(model)
        return await create_document(model, self._collection_name)

    async def update_model_by_id(self, model_id, data):
        valid_id = strict_bson_id_parser(model_id)
        model = Agent.model_validate(data.model_dump())
        await self._check_entities_exists(model)
        not_found_msg = f'Cannot update agent configuration with id {model_id}. Because no entity found.'
        await update_by_id(valid_id, model, self._collection_name, not_found_msg)

    async def delete_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        await delete_by_id(valid_id, self._collection_name)

    async def get_exported_agent_config_file_token(self, agent_id, generator):
        doc_agent = await self.get_model_by_id(agent_id)
        agent = Agent.model_validate(doc_agent)

        # Prepare for exporting
        encoding = DEFAULT_CHARSET
        folder_for_exporting = self.get_export_path(agent.id, "root")
        file_ext = ".zip"
        exported_file = folder_for_exporting.with_name(f'{folder_for_exporting.name}{file_ext}')
        file_info: FileInformation = {
            "name": f'{folder_for_exporting.name}_{get_datetime_now().strftime("%d-%m-%Y_%H-%M-%S")}{file_ext}',
            "path": str(exported_file.absolute().resolve()),
            "mime_type": "application/zip"
        }
        exported_file.unlink(missing_ok=True)

        # Write files
        config_obj = await self._get_agent_config(agent)
        _write_env_file(folder_for_exporting, config_obj)
        config_dir = self.get_export_path(agent.id, "config")
        config_dir.joinpath("config.json").write_text(jsonpickle.encode(config_obj, indent=2), encoding=encoding)

        zip_folder(folder_for_exporting, exported_file)
        shutil.rmtree(folder_for_exporting)  # remove folder after having zipped

        return generator.generate_token(file_info)

    async def _check_entities_exists(self, model: Agent):
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self._recognizer_service.get_model_by_id(model.image_recognizer_id))
                tg.create_task(self._chat_model_service.get_model_by_id(model.llm_id))
                tg.create_task(self._prompt_service.get_model_by_id(model.prompt_id))
                if model.retriever_ids is not None:
                    for retriever_id in model.retriever_ids:
                        tg.create_task(self._retriever_service.get_model_by_id(retriever_id))
                if model.mcp_server_ids is not None:
                    for server_id in model.mcp_server_ids:
                        tg.create_task(self._mcp_service.get_model_by_id(server_id))
        except ExceptionGroup as ex:
            self._logger.debug(ex)
            raise NotFoundError(reason="Some entities are not exists.")

    async def _get_agent_config(self, agent: Agent):
        dict_value: dict[str, Any] = {
            "agent_name": agent.name,
            "description": agent.description,
            "language": agent.language,
        }

        task_dict: dict[str, asyncio.Task | None] = {
            "image_recognizer": None,
            "retrievers": None,
            "embeddings": None,
            "tools": None,
            "mcp": None,
            "llm": None,
            "prompt": None,
        }
        async with asyncio.TaskGroup() as tg:
            if agent.image_recognizer_id:
                rec_id = agent.image_recognizer_id
                export_dir = self.get_export_path(agent.id, "recognizer")
                task_dict["image_recognizer"] = tg.create_task(
                    self._recognizer_service.get_configuration_by_id(rec_id, export_dir))
            if agent.retriever_ids and len(agent.retriever_ids) > 0:
                async def get_retrievers() -> list[RetrieverConfiguration]:
                    tasks: list[asyncio.Task] = []
                    retriever_export_dir = self.get_export_path(agent.id, "retriever")
                    async with asyncio.TaskGroup() as group:
                        for retriever_id in agent.retriever_ids:
                            task = group.create_task(
                                self._retriever_service.get_configuration_by_id(retriever_id, retriever_export_dir))
                            tasks.append(task)
                    return [task.result() for task in tasks]

                task_dict["retrievers"] = tg.create_task(get_retrievers())
            # if agent.tool_ids and len(agent.tool_ids) > 0:
            #     task_dict["tools"] = ""
            if agent.mcp_server_ids:
                async def get_mcp_configuration():
                    tasks: list[tuple[asyncio.Task, asyncio.Task]] = []
                    async with asyncio.TaskGroup() as group:
                        for server_id in agent.mcp_server_ids:
                            metadata_task = group.create_task(self._mcp_service.get_model_by_id(server_id))
                            config_task = group.create_task(self._mcp_service.get_configuration_by_id(server_id))
                            tasks.append((metadata_task, config_task))
                    servers: dict[str, MCPConnectionConfiguration] = {}
                    for metadata_task, config_task in tasks:
                        metadata: BaseMCPServer = metadata_task.result()
                        config = config_task.result()
                        servers[metadata.name] = config
                    return MCPConfiguration(connections=servers)

                task_dict["mcp"] = tg.create_task(get_mcp_configuration())
            task_dict["llm"] = tg.create_task(self._chat_model_service.get_configuration_by_id(agent.llm_id))
            task_dict["prompt"] = tg.create_task(self._prompt_service.get_configuration_by_id(agent.prompt_id))

        for k, v in task_dict.items():
            if v is not None:
                dict_value[k] = v.result()
        return AgentConfiguration.model_validate(dict_value)
