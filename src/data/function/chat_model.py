from abc import ABC, abstractmethod
from typing import Any

from ..base_model.chat_model import BaseChatModel
from ..database import get_by_id, MongoCollection, update_by_id, create_document, delete_by_id, get_collection
from ..dto.chat_model import ChatModelUpdate, ChatModelCreate, ChatModelPublic, GoogleGenAIChatModelPublic, \
    OllamaChatModelPublic
from ..model.chat_model import GoogleGenAIChatModel, OllamaChatModel, ChatModel
from ...config.model.chat_model import ChatModelConfiguration, ChatModelType
from ...config.model.chat_model.google_genai import GoogleGenAIChatModelConfiguration
from ...config.model.chat_model.ollama import OllamaChatModelConfiguration
from ...util import PagingParams, PagingWrapper
from ...util.error import InvalidArgumentError
from ...util.function import strict_bson_id_parser


# noinspection PyTypeHints
class IChatModelService(ABC):

    @abstractmethod
    async def get_all_models_with_paging(self, params: PagingParams,
                                         to_public: bool) -> PagingWrapper[ChatModel | ChatModelPublic]:
        """
        Retrieves all chat models as documents with pagination.

        Args:
            params: Pagination parameters.
            to_public: Whether to return public chat models.

        Returns:
            A PagingWrapper containing a list of ChatModel documents.
        """
        pass

    @abstractmethod
    async def get_model_by_id(self, model_id: str) -> ChatModel:
        """
        Retrieves a single chat model as a document by its ID.

        Args:
            model_id: The ID of the chat model.

        Returns:
            The ChatModel document.

        Raises:
            NotFoundError: If no chat model with the given ID is found.
        """
        pass

    @staticmethod
    @abstractmethod
    def convert_base_to_model(base_data: BaseChatModel) -> ChatModel:
        """
        Converts base chat model data into a specific ChatModel instance
        (e.g., GoogleGenAIChatModel, OllamaChatModel) based on its type.

        Args:
            base_data: The base chat model data.

        Returns:
            A specific ChatModel instance.

        Raises:
            InvalidArgumentError: If the chat model type is not supported.
        """
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_model(data: dict[str, Any]) -> ChatModel:
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_public(data: dict[str, Any]) -> ChatModelPublic:
        pass

    @abstractmethod
    async def get_configuration_by_id(self, model_id: str) -> ChatModelConfiguration:
        """
        Retrieves a chat model and converts it into an LLM configuration.

        Args:
            model_id: The ID of the chat model.

        Returns:
            An ChatModelConfiguration instance specific to the chat model type.

        Raises:
            NotFoundError: If no chat model with the given ID is found.
            InvalidArgumentError: If the LLM type is not supported for configuration.
        """
        pass

    @abstractmethod
    async def create_new(self, body: ChatModelCreate) -> str:
        """
        Creates a new chat model document.

        Args:
            body: The data for creating the chat model.

        Returns:
            The ID of the newly created chat model document.
        """
        pass

    @abstractmethod
    async def update_model_by_id(self, model_id: str, model: ChatModelUpdate) -> None:
        """
        Updates an existing chat model document.

        Args:
            model_id: The ID of the chat model to update.
            model: The updated chat model data.

        Raises:
            NotFoundError: If no chat model with the given ID is found.
        """
        pass

    @abstractmethod
    async def delete_model_by_id(self, model_id: str) -> None:
        """
        Deletes a chat model document by its ID.

        Args:
            model_id: The ID of the chat model to delete.

        Raises:
            NotFoundError: If no chat model with the given ID is found.
        """
        pass


class ChatModelServiceImpl(IChatModelService):
    def __init__(self):
        self._collection_name = MongoCollection.CHAT_MODEL

    async def get_all_models_with_paging(self, params, to_public):
        collection = get_collection(self._collection_name)
        map_func = self.convert_dict_to_public if to_public else self.convert_dict_to_model
        return await PagingWrapper.get_paging(params, collection, map_func)

    async def get_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'No chat model with id {model_id} found.'
        doc = await get_by_id(valid_id, self._collection_name, not_found_msg)
        return self.convert_dict_to_model(doc)

    @staticmethod
    def convert_base_to_model(base_data):
        dict_value = base_data.model_dump()
        if base_data.type == ChatModelType.GOOGLE_GENAI:
            return GoogleGenAIChatModel.model_validate(dict_value)
        elif base_data.type == ChatModelType.OLLAMA:
            return OllamaChatModel.model_validate(dict_value)
        else:
            raise InvalidArgumentError(f'Chat model type {base_data.type} is not supported.')

    @staticmethod
    def convert_dict_to_model(data: dict[str, Any]) -> ChatModel:
        data_type = data["type"]
        if data_type == ChatModelType.GOOGLE_GENAI.value:
            return GoogleGenAIChatModel.model_validate(data)
        elif data_type == ChatModelType.OLLAMA.value:
            return OllamaChatModel.model_validate(data)
        else:
            raise ValueError(f"Unsupported chat model type: {type(data)}")

    @staticmethod
    def convert_dict_to_public(data: dict[str, Any]) -> ChatModelPublic:
        data_type = data["type"]
        if data_type == ChatModelType.GOOGLE_GENAI.value:
            return GoogleGenAIChatModelPublic.model_validate(data)
        elif data_type == ChatModelType.OLLAMA.value:
            return OllamaChatModelPublic.model_validate(data)
        else:
            raise ValueError(f"Unsupported chat model type: {type(data)}")

    async def get_configuration_by_id(self, model_id):
        chat_model = await self.get_model_by_id(model_id)
        dict_value = chat_model.model_dump()
        if chat_model.type == ChatModelType.GOOGLE_GENAI:
            return GoogleGenAIChatModelConfiguration.model_validate(dict_value)
        elif chat_model.type == ChatModelType.OLLAMA:
            return OllamaChatModelConfiguration.model_validate(dict_value)
        else:
            raise InvalidArgumentError(f'LLM type {type(chat_model)} is not supported.')

    async def create_new(self, body) -> str:
        return await create_document(self.convert_base_to_model(body), self._collection_name)

    async def update_model_by_id(self, model_id, model):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'Cannot update chat model with id {model_id}. Because no chat model found.'
        await update_by_id(valid_id, model, self._collection_name, not_found_msg)

    async def delete_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        await delete_by_id(valid_id, self._collection_name)
