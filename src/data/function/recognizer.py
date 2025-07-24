import asyncio
import logging
from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import Any

from .file import IFileService
from ..base_model.recognizer import BaseRecognizer, RecognizerType, BaseImagePreprocessing, ImagePreprocessingType
from ..database import get_by_id, MongoCollection, update_by_id, delete_by_id, get_collection, create_document
from ..dto.recognizer import RecognizerUpdate, RecognizerCreate, RecognizerPublic, ImageRecognizerPublic
from ..model.recognizer import ImageRecognizer, Recognizer
from ...config.model.recognizer import RecognizerConfiguration, ClassDescriptor, RecognizerOutput
from ...config.model.recognizer.image import ImageRecognizerConfiguration, ImagePreprocessingConfiguration
from ...config.model.recognizer.image.preprocessing import ImageResizeConfiguration, ImageGrayscaleConfiguration, \
    ImagePadConfiguration
from ...util import PagingParams, PagingWrapper
from ...util.error import InvalidArgumentError, NotAcceptableError
from ...util.function import strict_bson_id_parser


class IRecognizerService(ABC):

    @abstractmethod
    async def get_all_models_with_paging(self, params: PagingParams,
                                         to_public: bool) -> PagingWrapper[Recognizer]:
        """
        Retrieves all recognizer models with pagination.

        Args:
            params: Pagination parameters.
            to_public: Whether to return public recognizer models.

        Returns:
            A PagingWrapper containing a list of Recognizer models.
        """
        pass

    @abstractmethod
    async def get_model_by_id(self, model_id: str) -> Recognizer:
        """
        Retrieves a recognizer model document by its ID.

        Args:
            model_id: The unique identifier of the recognizer model.

        Returns:
            A Recognizer object representing the model.

        Raises:
            NotFoundError: If no recognizer with the given ID is found.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_recognizer_type(base_data: BaseRecognizer) -> Recognizer:
        """
        Converts base recognizer data into a specific Recognizer instance
        (e.g., ImageRecognizer) based on its type.

        Args:
            base_data: The base recognizer data.

        Returns:
            A specific Recognizer instance.

        Raises:
            InvalidArgumentError: If the recognizer type is not supported.
        """
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_model(data: dict[str, Any]) -> Recognizer:
        pass

    @staticmethod
    @abstractmethod
    def convert_dict_to_public(data: dict[str, Any]) -> RecognizerPublic:
        pass

    @staticmethod
    @abstractmethod
    def get_preprocessing_configuration(base_data: BaseImagePreprocessing) -> ImagePreprocessingConfiguration:
        """
        Converts base image preprocessing data into a specific ImagePreprocessingConfiguration
        instance based on its type.

        Args:
            base_data: The base image preprocessing data.

        Returns:
            A specific ImagePreprocessingConfiguration instance.

        Raises:
            InvalidArgumentError: If the preprocessing type is not supported.
        """
        pass

    @abstractmethod
    async def get_configuration_by_id(self, recognizer_id: str,
                                      export_dir: str | PathLike[str]) -> RecognizerConfiguration:
        """
        Retrieves a recognizer model by its ID, fetches its associated model file,
        exports the file and output configuration to a specified directory,
        and converts it into a RecognizerConfiguration object.

        Args:
            recognizer_id: The unique identifier of the recognizer model.
            export_dir: The directory where the model file and output configuration will be exported.

        Returns:
            A RecognizerConfiguration object specific to the recognizer type.

        Raises:
            NotFoundError: If no recognizer or associated file with the given ID is found.
            InvalidArgumentError: If the recognizer type is not supported for configuration.
            IOError: If there's an issue with file system operations.
        """
        pass

    @abstractmethod
    async def create_new(self, body: RecognizerCreate) -> str:
        """
        Creates a new recognizer model.

        Args:
            body: The data for creating the new recognizer model.

        Returns:
            The ID of the newly created recognizer document.
        """
        pass

    @abstractmethod
    async def update_model_by_id(self, model_id: str, model: RecognizerUpdate) -> None:
        """
        Updates an existing recognizer model by its ID.

        Args:
            model_id: The unique identifier of the recognizer model to update.
            model: The updated data for the recognizer model.

        Raises:
            NotFoundError: If no recognizer with the given ID is found.
        """
        pass

    @abstractmethod
    async def delete_model_by_id(self, model_id: str) -> None:
        """
        Deletes a recognizer model by its ID.

        Args:
            model_id: The unique identifier of the recognizer model to delete.

        Raises:
            NotFoundError: If no recognizer with the given ID is found.
        """
        pass


class RecognizerServiceImpl(IRecognizerService):
    _logger = logging.getLogger(__name__)

    def __init__(self, file_service: IFileService):
        self._collection_name = MongoCollection.RECOGNIZER
        self._file_service = file_service

    async def get_all_models_with_paging(self, params, to_public):
        collection = get_collection(self._collection_name)
        map_func = self.convert_dict_to_public if to_public else self.convert_dict_to_model
        return await PagingWrapper.get_paging(params, collection, map_func)

    async def get_model_by_id(self, model_id):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'No recognizer with id {model_id} found.'
        doc = await get_by_id(valid_id, self._collection_name, not_found_msg)
        return self.convert_dict_to_model(doc)

    @staticmethod
    def get_recognizer_type(base_data: BaseRecognizer):
        if base_data.type == RecognizerType.IMAGE:
            return ImageRecognizer.model_validate(base_data.model_dump())
        else:
            raise InvalidArgumentError(f'Chat model type {base_data.type} is not supported.')

    @staticmethod
    def get_preprocessing_configuration(base_data):
        dict_value = base_data.model_dump()
        if base_data.type == ImagePreprocessingType.RESIZE:
            return ImageResizeConfiguration.model_validate(dict_value)
        elif base_data.type == ImagePreprocessingType.PAD:
            return ImagePadConfiguration.model_validate(dict_value)
        elif base_data.type == ImagePreprocessingType.GRAYSCALE:
            return ImageGrayscaleConfiguration.model_validate(dict_value)
        else:
            raise InvalidArgumentError(f'Preprocessing type {base_data.type} is not supported.')

    async def get_configuration_by_id(self, recognizer_id, export_dir):
        doc_recognizer = await self.get_model_by_id(recognizer_id)
        file_id: str = doc_recognizer.model_file_id
        file = await self._file_service.get_file_by_id(file_id)
        export_dir = Path(export_dir)
        export_dir.mkdir(exist_ok=True)

        file_data = Path(file.path).read_bytes()
        export_dir.joinpath(file.name).write_bytes(file_data)

        if doc_recognizer.type == RecognizerType.IMAGE:
            img_recognizer = ImageRecognizer.model_validate(doc_recognizer)

            output_file_name = "classes.json"
            descriptors = [ClassDescriptor.model_validate(c.model_dump()) for c in img_recognizer.output_classes]
            output_config = RecognizerOutput(classes=descriptors)
            export_dir.joinpath(output_file_name).write_text(output_config.model_dump_json(indent=2), encoding="utf-8")

            dict_value: dict[str, Any] = {
                "min_probability": img_recognizer.min_probability,
                "max_results": img_recognizer.max_results,
                "path": f'{export_dir.name}/{file.name}',
                "output_config_path": f'{export_dir.name}/{output_file_name}'
            }

            preprocessing_configs = img_recognizer.preprocessing_configs
            if preprocessing_configs and len(preprocessing_configs) != 0:
                dict_value["preprocessing"] = [self.get_preprocessing_configuration(c) for c in preprocessing_configs]

            return ImageRecognizerConfiguration.model_validate(dict_value)
        else:
            raise InvalidArgumentError(f'LLM type {type(doc_recognizer)} is not supported.')

    @staticmethod
    def convert_dict_to_model(data):
        data_type = data["type"]
        if data_type == RecognizerType.IMAGE.value:
            return ImageRecognizer.model_validate(data)
        else:
            raise ValueError(f"Unsupported recognizer type: {type(data)}")

    @staticmethod
    def convert_dict_to_public(data):
        data_type = data["type"]
        if data_type == RecognizerType.IMAGE.value:
            return ImageRecognizerPublic.model_validate(data)
        else:
            raise ValueError(f"Unsupported recognizer type: {type(data)}")

    async def create_new(self, body):
        return await create_document(self.get_recognizer_type(body), self._collection_name)

    async def update_model_by_id(self, model_id, model):
        valid_id = strict_bson_id_parser(model_id)
        not_found_msg = f'Cannot update recognizer with id {model_id}. Because no recognizer found.'
        await update_by_id(valid_id, model, self._collection_name, not_found_msg)

    async def delete_model_by_id(self, model_id: str) -> None:
        valid_id = strict_bson_id_parser(model_id)
        doc = await get_by_id(valid_id, self._collection_name)
        if doc is None:
            return

        # Check Agent using
        collection = get_collection(MongoCollection.AGENT)
        agent_using_doc = await collection.find_one({"image_recognizer_id": model_id})
        if agent_using_doc is not None:
            raise NotAcceptableError(f"Cannot delete recognizer with id {model_id}. "
                                     f"Agent with id {agent_using_doc["_id"]} is still using it.")

        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self._file_service.delete_file_by_id(doc["model_file_id"]))
                tg.create_task(delete_by_id(valid_id, self._collection_name))
        except ExceptionGroup as e:
            self._logger.debug(e)
            return
