from abc import ABC, abstractmethod
from typing import Any

from ..database import get_by_id, MongoCollection, get_collection, create_document, update_by_id, delete_by_id
from ..dto.prompt import PromptCreate, PromptUpdate, PromptPublic
from ..model import Prompt
from ...config.model.prompt import PromptConfiguration
from ...util import PagingWrapper, PagingParams
from ...util.function import strict_bson_id_parser


class IPromptService(ABC):

    @abstractmethod
    async def get_all_models_with_paging(self, params: PagingParams,
                                         to_public: bool) -> PagingWrapper[Prompt]:
        """
        Retrieves all prompt configurations with pagination.

        Args:
            params: Pagination parameters.
            to_public: Whether to return public prompt configurations.

        Returns:
            A PagingWrapper containing a list of PromptPublic objects.
        """
        pass

    @abstractmethod
    async def get_model_by_id(self, model_id: str) -> Prompt:
        """
        Retrieves a prompt document by its ID.

        Args:
            model_id: The unique identifier of the prompt.

        Returns:
            The raw prompt document.

        Raises:
            NotFoundError: If no prompt configuration with the given ID is found.
        """
        pass

    @abstractmethod
    async def get_configuration_by_id(self, model_id: str) -> PromptConfiguration:
        """
        Retrieves a prompt document by its ID and converts it into a PromptConfiguration object.

        Args:
            model_id: The unique identifier of the prompt.

        Returns:
            A PromptConfiguration object.

        Raises:
            NotFoundError: If no prompt configuration with the given ID is found.
            ValidationError: If the document cannot be validated into a PromptConfiguration.
        """
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_model(data: dict[str, Any]) -> Prompt:
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_public(data: dict[str, Any]) -> PromptPublic:
        pass

    @abstractmethod
    async def create_new(self, data: PromptCreate) -> str:
        """
        Creates a new prompt configuration.

        Args:
            data: The data for creating the new prompt.

        Returns:
            The ID of the newly created prompt document.
        """
        pass

    @abstractmethod
    async def update_model_by_id(self, model_id: str, data: PromptUpdate) -> None:
        """
        Updates an existing prompt configuration by its ID.

        Args:
            model_id: The unique identifier of the prompt to update.
            data: The updated data for the prompt.

        Raises:
            NotFoundError: If no prompt configuration with the given ID is found.
        """
        pass

    @abstractmethod
    async def delete_model_by_id(self, model_id: str) -> None:
        """
        Deletes a prompt configuration by its ID.

        Args:
            model_id: The unique identifier of the prompt to delete.

        Raises:
            NotFoundError: If no prompt configuration with the given ID is found.
        """
        pass


class PromptServiceImpl(IPromptService):
    def __init__(self):
        self._collection_name = MongoCollection.PROMPT

    async def get_all_models_with_paging(self, params, to_public):
        collection = get_collection(self._collection_name)
        map_func = self.convert_dict_to_public if to_public else self.convert_dict_to_model
        return await PagingWrapper.get_paging(params, collection, map_func)

    async def get_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'No prompt configuration with id {model_id} found.'
        doc = await get_by_id(valid_id, self._collection_name, not_found_msg)
        return self.convert_dict_to_model(doc)

    async def get_configuration_by_id(self, model_id):
        doc_prompt = await self.get_model_by_id(model_id)
        prompt = Prompt.model_validate(doc_prompt)
        return PromptConfiguration.model_validate(prompt.model_dump())

    @staticmethod
    def convert_dict_to_model(data):
        return Prompt.model_validate(data)

    @staticmethod
    def convert_dict_to_public(data):
        return PromptPublic.model_validate(data)

    async def create_new(self, data):
        model = Prompt.model_validate(data.model_dump())
        return await create_document(model, self._collection_name)

    async def update_model_by_id(self, model_id, data):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'Cannot update prompt configuration with id {model_id}. Because no prompt configuration found.'
        await update_by_id(valid_id, data, self._collection_name, not_found_msg)

    async def delete_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        await delete_by_id(valid_id, self._collection_name)
