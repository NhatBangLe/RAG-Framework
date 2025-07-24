from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import cast, Any

from .embeddings import IEmbeddingsService
from .file import IFileService
from ..base_model.retriever import BaseRetriever, RetrieverType
from ..database import get_by_id, MongoCollection, update_by_id, delete_by_id, get_collection, create_document
from ..dto.retriever import RetrieverUpdate, RetrieverCreate, RetrieverPublic, BM25RetrieverPublic, \
    ChromaRetrieverPublic, VectorStorePublic
from ..model.retriever import Retriever, BM25Retriever, ChromaRetriever
from ...config.model.data import ExternalDocumentConfiguration, ExternalDocument
from ...config.model.retriever import RetrieverConfiguration
from ...config.model.retriever.bm25 import BM25Configuration
from ...config.model.retriever.vector_store.chroma import ChromaVSConfiguration
from ...util import PagingWrapper, PagingParams, DEFAULT_CHARSET
from ...util.error import InvalidArgumentError
from ...util.function import strict_bson_id_parser


# noinspection PyTypeHints
class IRetrieverService(ABC):
    """
    Interface for managing retriever models.
    Defines the contract for services that interact with retriever data.
    """

    @abstractmethod
    async def get_all_models_with_paging(self, params: PagingParams,
                                         to_public: bool) -> PagingWrapper[Retriever | RetrieverPublic]:
        """
        Retrieves all retriever models with pagination.

        Args:
            params: Pagination parameters.
            to_public: Whether to convert the models to public format.

        Returns:
            A PagingWrapper containing a list of models.
        """
        pass

    @abstractmethod
    async def get_model_by_id(self, model_id: str) -> Retriever:
        """
        Retrieves a retriever model document by its ID.

        Args:
            model_id: The unique identifier of the retriever model.

        Returns:
            A Retriever object representing the model.

        Raises:
            NotFoundError: If no retriever with the given ID is found.
        """
        pass

    @abstractmethod
    async def get_configuration_by_id(self, model_id: str, export_dir: str | PathLike[str]) -> RetrieverConfiguration:
        """
        Retrieves a retriever model by its ID and converts it into a
        RetrieverConfiguration object.

        Args:
            model_id: The unique identifier of the retriever model.
            export_dir: The directory to export files to, if applicable.

        Returns:
            A RetrieverConfiguration object.

        Raises:
            NotFoundError: If no retriever with the given ID is found.
            ValidationError: If the document cannot be validated into a RetrieverConfiguration.
        """
        pass

    @staticmethod
    @abstractmethod
    def convert_base_to_model(base_retriever: BaseRetriever) -> Retriever:
        """
        Converts base retriever data into a specific Retriever model instance
        (e.g., BM25Retriever, ChromaRetriever) based on its type.

        Args:
            base_retriever: The base retriever data.

        Returns:
            A specific Retriever instance.

        Raises:
            InvalidArgumentError: If the retriever type is not supported.
        """
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_model(data: dict[str, Any]) -> Retriever:
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_public(data: dict[str, Any]) -> RetrieverPublic:
        pass

    @abstractmethod
    async def create_new(self, data: RetrieverCreate) -> str:
        """
        Creates a new retriever model.

        Args:
            data: The data for creating the new retriever model.

        Returns:
            The ID of the newly created retriever document.
        """
        pass

    @abstractmethod
    async def update_model_by_id(self, model_id: str, data: RetrieverUpdate) -> None:
        """
        Updates an existing retriever model by its ID.

        Args:
            model_id: The unique identifier of the retriever model to update.
            data: The updated data for the retriever model.

        Raises:
            NotFoundError: If no retriever with the given ID is found.
        """
        pass

    @abstractmethod
    async def delete_model_by_id(self, model_id: str) -> None:
        """
        Deletes a retriever model by its ID.

        Args:
            model_id: The unique identifier of the retriever model to delete.

        Raises:
            NotFoundError: If no retriever with the given ID is found.
        """
        pass


class RetrieverServiceImpl(IRetrieverService):
    def __init__(self, embeddings_service: IEmbeddingsService, file_service: IFileService):
        self._collection_name = MongoCollection.RETRIEVER
        self._embeddings_service = embeddings_service
        self._file_service = file_service

    async def get_all_models_with_paging(self, params, to_public):
        collection = get_collection(self._collection_name)
        map_func = self.convert_dict_to_public if to_public else self.convert_dict_to_model
        return await PagingWrapper.get_paging(params, collection, map_func)

    async def get_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'No retriever with id {model_id} found.'
        doc = await get_by_id(valid_id, self._collection_name, not_found_msg)
        return self.convert_dict_to_model(doc)

    async def get_configuration_by_id(self, model_id, export_dir):
        doc_retriever = await self.get_model_by_id(model_id)
        if doc_retriever.type == RetrieverType.BM25:
            retriever = cast(BM25Retriever, doc_retriever)
            return await self._get_bm25_configuration(retriever, export_dir)
        elif doc_retriever.type == RetrieverType.CHROMA_DB:
            retriever = cast(ChromaRetriever, doc_retriever)
            return await self._get_chroma_vs_configuration(retriever, export_dir)
        else:
            raise InvalidArgumentError(f'Retriever type {doc_retriever.type} is not supported.')

    async def _get_bm25_configuration(self, retriever: BM25Retriever, export_dir: str | PathLike[str]):
        dict_value = retriever.model_dump()
        dict_value["embeddings_model"] = await self._embeddings_service.get_configuration_by_id(retriever.embeddings_id)

        # Copy a file contains removal words to export_dir
        removal_words_file_id = retriever.removal_words_file_id
        if removal_words_file_id:
            removal_words_file = await self._file_service.get_file_by_id(removal_words_file_id)
            export_dir = Path(export_dir)
            export_dir.mkdir(parents=True, exist_ok=True)
            file_data = Path(removal_words_file.path).read_bytes()
            export_dir.joinpath(removal_words_file.name).write_bytes(file_data)
            dict_value["removal_words_path"] = f'{export_dir.name}/{removal_words_file.name}'

        return BM25Configuration.model_validate(dict_value)

    async def _get_chroma_vs_configuration(self, retriever: ChromaRetriever, export_dir: str | PathLike[str]):
        dict_value = retriever.model_dump()
        dict_value["embeddings_model"] = await self._embeddings_service.get_configuration_by_id(retriever.embeddings_id)
        del dict_value["type"]
        del dict_value["embeddings_id"]

        # Dump JSON file of external documents in export_dir
        external_data = retriever.external_data
        if external_data and len(external_data) > 0:
            export_dir = Path(export_dir)
            export_dir.mkdir(parents=True, exist_ok=True)
            external_data_path = export_dir.joinpath(f"{retriever.name}_external_data.json")
            documents = [ExternalDocument.model_validate(d.model_dump()) for d in external_data]
            ext_docs_conf = ExternalDocumentConfiguration(version="0.0.1", documents=documents)
            external_data_path.write_text(ext_docs_conf.model_dump_json(indent=2), encoding=DEFAULT_CHARSET)
            dict_value["external_data_config_path"] = f'{export_dir.name}/{external_data_path.name}'

        return ChromaVSConfiguration.model_validate(dict_value)

    @staticmethod
    def convert_base_to_model(base_retriever):
        if base_retriever.type == RetrieverType.BM25:
            return BM25Retriever.model_validate(base_retriever.model_dump())
        elif base_retriever.type == RetrieverType.CHROMA_DB:
            return ChromaRetriever.model_validate(base_retriever.model_dump())
        else:
            raise InvalidArgumentError(f'Retriever type {base_retriever.type} is not supported.')

    @staticmethod
    def convert_dict_to_public(data: dict[str, Any]) -> VectorStorePublic | RetrieverPublic:
        data_type = data["type"]
        if data_type == RetrieverType.BM25.value:
            return BM25RetrieverPublic.model_validate(data)
        elif data_type == RetrieverType.CHROMA_DB.value:
            return ChromaRetrieverPublic.model_validate(data)
        else:
            raise ValueError(f"Unsupported recognizer type: {type(data)}")

    @staticmethod
    def convert_dict_to_model(data: dict[str, Any]) -> Retriever:
        data_type = data["type"]
        if data_type == RetrieverType.BM25.value:
            return BM25Retriever.model_validate(data)
        elif data_type == RetrieverType.CHROMA_DB.value:
            return ChromaRetriever.model_validate(data)
        else:
            raise ValueError(f"Unsupported recognizer type: {type(data)}")

    async def create_new(self, data):
        model = self.convert_base_to_model(data)
        if isinstance(model, BM25Retriever):
            embeddings_id = model.embeddings_id
            await self._embeddings_service.get_model_by_id(embeddings_id)
        elif isinstance(model, ChromaRetriever):
            embeddings_id = model.embeddings_id
            await self._embeddings_service.get_model_by_id(embeddings_id)
        return await create_document(model, self._collection_name)

    async def update_model_by_id(self, model_id, data):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'Cannot update retriever with id {model_id}. Because no retriever found.'
        await update_by_id(valid_id, data, self._collection_name, not_found_msg)

    async def delete_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        await delete_by_id(valid_id, self._collection_name)
