from abc import ABC, abstractmethod

from ..base_model.chat_model import BaseChatModel, ChatModelType
from ..database import get_by_id, MongoCollection, update_by_id, create_document, delete_by_id, get_collection
from ..dto.chat_model import ChatModelUpdate, ChatModelCreate
from ..model.chat_model import GoogleGenAIChatModel, OllamaChatModel, ChatModel
from ...config.model.chat_model import LLMConfiguration
from ...config.model.chat_model.google_genai import GoogleGenAILLMConfiguration
from ...config.model.chat_model.ollama import OllamaLLMConfiguration
from ...util import PagingParams, PagingWrapper
from ...util.error import InvalidArgumentError


# noinspection PyTypeHints
class IChatModelService(ABC):

    @abstractmethod
    async def get_all_models_with_paging(self, params: PagingParams) -> PagingWrapper[ChatModel]:
        """
        Retrieves all chat models as documents with pagination.

        Args:
            params: Pagination parameters.

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
    def convert_into_model(base_data: BaseChatModel) -> ChatModel:
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

    @abstractmethod
    async def get_configuration_by_id(self, model_id: str) -> LLMConfiguration:
        """
        Retrieves a chat model and converts it into an LLM configuration.

        Args:
            model_id: The ID of the chat model.

        Returns:
            An LLMConfiguration instance specific to the chat model type.

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

    async def get_all_models_with_paging(self, params):
        collection = get_collection(self._collection_name)
        return await PagingWrapper.get_paging(params, collection)

    async def get_model_by_id(self, model_id):
        not_found_msg = f'No chat model with id {model_id} found.'
        return await get_by_id(model_id, self._collection_name, not_found_msg)

    @staticmethod
    def convert_into_model(base_data):
        dict_value = base_data.model_dump()
        if base_data.type == ChatModelType.GOOGLE_GENAI:
            return GoogleGenAIChatModel.model_validate(dict_value)
        elif base_data.type == ChatModelType.OLLAMA:
            return OllamaChatModel.model_validate(dict_value)
        else:
            raise InvalidArgumentError(f'Chat model type {base_data.type} is not supported.')

    async def get_configuration_by_id(self, model_id):
        doc_chat_model = await self.get_model_by_id(model_id)
        if doc_chat_model.type == ChatModelType.GOOGLE_GENAI:
            return GoogleGenAILLMConfiguration.model_validate(doc_chat_model)
        elif doc_chat_model.type == ChatModelType.OLLAMA:
            return OllamaLLMConfiguration.model_validate(doc_chat_model)
        else:
            raise InvalidArgumentError(f'LLM type {type(doc_chat_model)} is not supported.')

    async def create_new(self, body) -> str:
        return await create_document(self.convert_into_model(body), self._collection_name)

    async def update_model_by_id(self, model_id, model):
        not_found_msg = f'Cannot update chat model with id {model_id}. Because no chat model found.'
        await update_by_id(model_id, model, self._collection_name, not_found_msg)

    async def delete_model_by_id(self, model_id):
        await delete_by_id(model_id, self._collection_name)
