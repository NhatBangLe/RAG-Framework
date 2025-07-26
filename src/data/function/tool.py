from abc import ABC, abstractmethod
from typing import Any

from ..base_model.tool import BaseTool
from ..database import get_by_id, MongoCollection, update_by_id, create_document, delete_by_id, get_collection
from ..dto.tool import ToolCreate, ToolUpdate, ToolPublic, DuckDuckGoSearchToolPublic
from ..model.tool import Tool, DuckDuckGoSearchTool
from ...config.model.tool import ToolConfiguration
from ...config.model.tool.search import SearchToolType
from ...config.model.tool.search.duckduckgo import DuckDuckGoSearchToolConfiguration
from ...util import PagingParams, PagingWrapper
from ...util.error import InvalidArgumentError, NotAcceptableError
from ...util.function import strict_bson_id_parser


class IToolService(ABC):

    @abstractmethod
    async def get_all_models_with_paging(self, params: PagingParams,
                                         to_public: bool) -> PagingWrapper:
        """
        Retrieves all tools as documents with pagination.

        Args:
            params: Pagination parameters.
            to_public: Whether to return public tools.

        Returns:
            A PagingWrapper containing a list of BaseTool documents.
        """
        pass

    @abstractmethod
    async def get_model_by_id(self, model_id: str) -> Tool:
        """
        Retrieves a single tool as a document by its ID.

        Args:
            model_id: The ID of the tool.

        Returns:
            The ChatModel document.

        Raises:
            NotFoundError: If no tool with the given ID is found.
        """
        pass

    @staticmethod
    @abstractmethod
    def convert_base_to_model(base_data: BaseTool) -> Tool:
        """
        Converts base tool data into a specific Tool instance based on its type.

        Args:
            base_data: The base tool data.

        Returns:
            A specific Tool instance.

        Raises:
            InvalidArgumentError: If the tool type is not supported.
        """
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_model(data: dict[str, Any]) -> Tool:
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_public(data: dict[str, Any]) -> ToolPublic:
        pass

    @abstractmethod
    async def get_configuration_by_id(self, model_id: str) -> ToolConfiguration:
        """
        Retrieves a tool and converts it into a ToolConfiguration instance based on its type.

        Args:
            model_id: The ID of the tool.

        Returns:
            An ToolConfiguration instance specific to the tool type.

        Raises:
            NotFoundError: If no tool with the given ID is found.
            InvalidArgumentError: If the tool type is not supported for configuration.
        """
        pass

    @abstractmethod
    async def create_new(self, body: ToolCreate) -> str:
        """
        Creates a new tool document.

        Args:
            body: The data for creating the tool.

        Returns:
            The ID of the newly created tool document.
        """
        pass

    @abstractmethod
    async def update_model_by_id(self, model_id: str, model: ToolUpdate) -> None:
        """
        Updates an existing tool document.

        Args:
            model_id: The ID of the tool to update.
            model: The updated tool data.

        Raises:
            NotFoundError: If no tool with the given ID is found.
        """
        pass

    @abstractmethod
    async def delete_model_by_id(self, model_id: str) -> None:
        """
        Deletes a tool document by its ID.

        Args:
            model_id: The ID of the tool to delete.

        Raises:
            NotFoundError: If no tool with the given ID is found.
        """
        pass


class ToolServiceImpl(IToolService):
    def __init__(self):
        self._collection_name = MongoCollection.TOOL

    async def get_all_models_with_paging(self, params, to_public):
        collection = get_collection(self._collection_name)
        map_func = self.convert_dict_to_public if to_public else self.convert_dict_to_model
        return await PagingWrapper.get_paging(params, collection, map_func)

    async def get_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'No tool with id {model_id} found.'
        doc = await get_by_id(valid_id, self._collection_name, not_found_msg)
        return self.convert_dict_to_model(doc)

    @staticmethod
    def convert_base_to_model(base_data):
        dict_value = base_data.model_dump()
        obj_type = dict_value["type"]
        if obj_type == SearchToolType.DUCKDUCKGO_SEARCH.value:
            return DuckDuckGoSearchTool.model_validate(dict_value)
        else:
            raise InvalidArgumentError(f'Tool type {obj_type} is not supported.')

    @staticmethod
    def convert_dict_to_model(data):
        obj_type = data["type"]
        if obj_type == SearchToolType.DUCKDUCKGO_SEARCH.value:
            return DuckDuckGoSearchTool.model_validate(data)
        else:
            raise InvalidArgumentError(f'Tool type {obj_type} is not supported.')

    @staticmethod
    def convert_dict_to_public(data):
        obj_type = data["type"]
        if obj_type == SearchToolType.DUCKDUCKGO_SEARCH.value:
            return DuckDuckGoSearchToolPublic.model_validate(data)
        else:
            raise InvalidArgumentError(f'Tool type {obj_type} is not supported.')

    async def get_configuration_by_id(self, model_id):
        chat_model = await self.get_model_by_id(model_id)
        dict_value = chat_model.model_dump()
        data_type = dict_value["type"]
        if data_type == SearchToolType.DUCKDUCKGO_SEARCH.value:
            return DuckDuckGoSearchToolConfiguration.model_validate(dict_value)
        else:
            raise InvalidArgumentError(f'Tool type {data_type} is not supported.')

    async def create_new(self, body) -> str:
        return await create_document(self.convert_base_to_model(body), self._collection_name)

    async def update_model_by_id(self, model_id, model):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'Cannot update tool with id {model_id}. Because no tool found.'
        await update_by_id(valid_id, model, self._collection_name, not_found_msg)

    async def delete_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        doc = await get_by_id(valid_id, self._collection_name)
        if doc is None:
            return

        # Check Agent using
        collection = get_collection(MongoCollection.AGENT)
        agent_using_doc = await collection.find_one({"tool_ids": model_id})
        if agent_using_doc is not None:
            raise NotAcceptableError(f"Cannot delete tool with id {model_id}. "
                                     f"Agent with id {agent_using_doc["_id"]} is still using it.")

        await delete_by_id(valid_id, self._collection_name)
