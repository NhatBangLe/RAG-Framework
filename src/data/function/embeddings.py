from abc import ABC, abstractmethod

from ..base_model.embeddings import BaseEmbeddings, EmbeddingsType
from ..database import MongoCollection, update_by_id, delete_by_id, get_collection, get_by_id, create_document
from ..dto.embeddings import EmbeddingsCreate, EmbeddingsUpdate
from ..model.embeddings import GoogleGenAIEmbeddings, HuggingFaceEmbeddings, Embeddings
from ...config.model.embeddings import EmbeddingsConfiguration
from ...util import PagingWrapper, PagingParams
from ...util.error import InvalidArgumentError


# noinspection PyTypeHints
class IEmbeddingsService(ABC):

    @abstractmethod
    async def get_all_models_with_paging(self, params: PagingParams) -> PagingWrapper[Embeddings]:
        """
        Retrieves all embedding models with pagination.

        Args:
            params: Pagination parameters.

        Returns:
            A PagingWrapper containing a list of Embeddings models.
        """
        pass

    @abstractmethod
    async def get_model_by_id(self, model_id: str) -> Embeddings:
        """
        Retrieves an embeddings model document by its ID.

        Args:
            model_id: The unique identifier of the embedding model.

        Returns:
            The raw embeddings model a document (e.g., a dictionary).

        Raises:
            NotFoundError: If no embedding model with the given ID is found.
        """
        pass

    @abstractmethod
    async def get_configuration_by_id(self, model_id: str) -> EmbeddingsConfiguration:
        """
        Retrieves an embedding model by its ID and converts it into an
        EmbeddingsConfiguration object.

        Args:
            model_id: The unique identifier of the embedding model.

        Returns:
            An EmbeddingsConfiguration object.

        Raises:
            NotFoundError: If no embedding model with the given ID is found.
            ValidationError: If the document cannot be validated into an EmbeddingsConfiguration.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_model(base_data: BaseEmbeddings) -> Embeddings:
        """
        Converts base embeddings data into a specific Embeddings model instance
        (e.g., GoogleGenAIEmbeddings, HuggingFaceEmbeddings) based on its type.

        Args:
            base_data: The base embeddings data.

        Returns:
            A specific Embeddings instance.

        Raises:
            InvalidArgumentError: If the embedding type is not supported.
        """
        pass

    @abstractmethod
    async def create_new(self, data: EmbeddingsCreate) -> str:
        """
        Creates a new embeddings model.

        Args:
            data: The data for creating the new embeddings model.

        Returns:
            The ID of the newly created embeddings document.
        """
        pass

    @abstractmethod
    async def update_model_by_id(self, model_id: str, data: EmbeddingsUpdate) -> None:
        """
        Updates an existing embeddings model by its ID.

        Args:
            model_id: The unique identifier of the embedding model to update.
            data: The updated data for the embedding model.

        Raises:
            NotFoundError: If no embedding model with the given ID is found.
        """
        pass

    @abstractmethod
    async def delete_model_by_id(self, model_id: str) -> None:
        """
        Deletes an embedding model by its ID.

        Args:
            model_id: The unique identifier of the embedding model to delete.

        Raises:
            NotFoundError: If no embedding model with the given ID is found.
        """
        pass


class EmbeddingsServiceImpl(IEmbeddingsService):
    def __init__(self):
        self._collection_name = MongoCollection.EMBEDDINGS

    async def get_all_models_with_paging(self, params):
        collection = get_collection(self._collection_name)
        return await PagingWrapper.get_paging(params, collection)

    async def get_model_by_id(self, model_id):
        not_found_msg = f'No embeddings model with id {model_id} found.'
        return await get_by_id(model_id, self._collection_name, not_found_msg)

    async def get_configuration_by_id(self, model_id) -> EmbeddingsConfiguration:
        pass

    @staticmethod
    def get_model(base_data):
        if base_data.type == EmbeddingsType.GOOGLE_GENAI:
            return GoogleGenAIEmbeddings.model_validate(base_data.model_dump())
        elif base_data.type == EmbeddingsType.HUGGING_FACE:
            return HuggingFaceEmbeddings.model_validate(base_data.model_dump())
        else:
            raise InvalidArgumentError(f'Embeddings type {base_data.type} is not supported.')

    async def create_new(self, data):
        return await create_document(self.get_model(data), self._collection_name)

    async def update_model_by_id(self, model_id, data):
        not_found_msg = f'Cannot update embeddings model with id {model_id}. Because no embeddings model found.'
        await update_by_id(model_id, data, self._collection_name, not_found_msg)

    async def delete_model_by_id(self, model_id):
        await delete_by_id(model_id, self._collection_name)
