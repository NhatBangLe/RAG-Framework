from abc import ABC, abstractmethod
from typing import Any

from ..database import get_by_id, MongoCollection, update_by_id, delete_by_id, get_collection, create_document
from ..dto.mcp import MCPUpdate, MCPCreate, MCPPublic, MCPStreamableServerPublic, MCPStdioServerPublic
from ..model.mcp import MCP, MCPStreamableServer, MCPStdioServer
from ...config.model.mcp import MCPConnectionConfiguration, MCPTransport, \
    StreamableConnectionConfiguration, StdioConnectionConfiguration
from ...util import PagingWrapper, PagingParams
from ...util.function import strict_bson_id_parser


# noinspection PyTypeHints
class IMCPService(ABC):

    @abstractmethod
    async def get_all_models_with_paging(self, params: PagingParams,
                                         to_public: bool) -> PagingWrapper[MCP]:
        """
        Retrieves all MCP configurations with pagination.

        Args:
            params: Pagination parameters.
            to_public: Whether to return public MCP configurations.

        Returns:
            A PagingWrapper containing a list of MCPPublic objects.
        """
        pass

    @abstractmethod
    async def get_model_by_id(self, model_id: str) -> MCP:
        """
        Retrieves an MCP configuration document by its ID.

        Args:
            model_id: The unique identifier of the MCP configuration.

        Returns:
            An MCP object representing the configuration.

        Raises:
            NotFoundError: If no MCP configuration with the given ID is found.
        """
        pass

    @abstractmethod
    async def get_configuration_by_id(self, model_id: str) -> MCPConnectionConfiguration:
        """
        Retrieves an MCP configuration by its ID and transforms it into a
        structured MCPConfiguration object with connections.

        Args:
            model_id: The unique identifier of the MCP configuration.

        Returns:
            An MCPConfiguration object.

        Raises:
            NotFoundError: If no MCP configuration with the given ID is found.
            ValidationError: If the document cannot be validated into an MCPConfiguration.
        """
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_model(data: dict[str, Any]) -> MCP:
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_public(data: dict[str, Any]) -> MCPPublic:
        pass

    @abstractmethod
    async def create_new(self, data: MCPCreate) -> str:
        """
        Creates a new MCP configuration.

        Args:
            data: The data for creating the new MCP configuration.

        Returns:
            The ID of the newly created MCP document.
        """
        pass

    @abstractmethod
    async def update_model_by_id(self, model_id: str, data: MCPUpdate) -> None:
        """
        Updates an existing MCP configuration by its ID.

        Args:
            model_id: The unique identifier of the MCP configuration to update.
            data: The updated data for the MCP configuration.

        Raises:
            NotFoundError: If no MCP configuration with the given ID is found.
        """
        pass

    @abstractmethod
    async def delete_model_by_id(self, model_id: str) -> None:
        """
        Deletes an MCP configuration by its ID.

        Args:
            model_id: The unique identifier of the MCP configuration to delete.

        Raises:
            NotFoundError: If no MCP configuration with the given ID is found.
        """
        pass


class MCPServiceImpl(IMCPService):
    def __init__(self):
        self._collection_name = MongoCollection.MCP

    async def get_all_models_with_paging(self, params, to_public):
        collection = get_collection(self._collection_name)
        map_func = self.convert_dict_to_public if to_public else self.convert_dict_to_model
        return await PagingWrapper.get_paging(params, collection, map_func)

    async def get_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'No MCP configuration with id {model_id} found.'
        doc = await get_by_id(valid_id, self._collection_name, not_found_msg)
        return self.convert_dict_to_model(doc)

    async def get_configuration_by_id(self, model_id):
        doc_mcp = await self.get_model_by_id(model_id)
        dict_value = doc_mcp.model_dump()
        if doc_mcp.type == MCPTransport.STREAMABLE_HTTP:
            return StreamableConnectionConfiguration.model_validate(dict_value)
        elif doc_mcp.type == MCPTransport.STDIO:
            return StdioConnectionConfiguration.model_validate(dict_value)
        else:
            raise ValueError(f'MCP transport type {doc_mcp.type} is not supported.')

    @staticmethod
    def convert_dict_to_model(data):
        data_type = data["type"]
        if data_type == MCPTransport.STREAMABLE_HTTP.value:
            return MCPStreamableServer.model_validate(data)
        elif data_type == MCPTransport.STDIO.value:
            return MCPStdioServer.model_validate(data)
        else:
            raise ValueError(f"Unsupported MCP transport type: {data_type}")

    @staticmethod
    def convert_dict_to_public(data):
        data_type = data["type"]
        if data_type == MCPTransport.STREAMABLE_HTTP.value:
            return MCPStreamableServerPublic.model_validate(data)
        elif data_type == MCPTransport.STDIO.value:
            return MCPStdioServerPublic.model_validate(data)
        else:
            raise ValueError(f"Unsupported MCP transport type: {data_type}")

    async def create_new(self, data):
        return await create_document(data, self._collection_name)

    async def update_model_by_id(self, model_id, data):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'Cannot update MCP configuration with id {model_id}. Because no MCP configuration found.'
        await update_by_id(valid_id, data, self._collection_name, not_found_msg)

    async def delete_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        await delete_by_id(valid_id, self._collection_name)
