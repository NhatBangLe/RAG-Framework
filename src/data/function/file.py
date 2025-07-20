import asyncio
import os
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from ..database import get_by_id, MongoCollection, create_document, delete_by_id
from ..model import File
from ...util.constant import EnvVar


class IFileService(ABC):

    @abstractmethod
    async def get_file_by_id(self, file_id: str) -> File:
        """
        Retrieves file metadata by its ID.

        Args:
            file_id: The unique identifier of the file.

        Returns:
            A File object containing the file's metadata.

        Raises:
            NotFoundError: If no file with the given ID is found.
        """
        pass

    @abstractmethod
    async def save_file(self, file: UploadFile) -> str:
        """
        Saves an uploaded file to local storage and records its metadata in the database.

        Args:
            file: An UploadFile object containing the file's content and metadata.

        Returns:
            The ID of the newly saved file record.
        """
        pass

    @abstractmethod
    async def delete_file_by_id(self, file_id: str) -> None:
        """
        Deletes a file from local storage and its corresponding record from the database.

        Args:
            file_id: The ID of the file to delete.

        Raises:
            NotFoundError: If no file with the given ID is found.
        """
        pass


class FileServiceImpl(IFileService):
    def __init__(self):
        self._collection_name = MongoCollection.FILE

    async def get_file_by_id(self, file_id):
        not_found_msg = f'No file with id {file_id} found.'
        doc = await get_by_id(file_id, self._collection_name, not_found_msg)
        return File.model_validate(doc)

    async def save_file(self, file):
        save_path = Path(os.getenv(EnvVar.LOCAL_FILE_DIR.value, "/app/local"), str(uuid4()))
        file_record = File(name=file.filename, mime_type=file.content_type, path=str(save_path))
        async with asyncio.TaskGroup() as tg:
            content_task = tg.create_task(file.read())
            save_record_task = tg.create_task(create_document(file_record, self._collection_name))
        save_path.write_bytes(content_task.result())
        return save_record_task.result()

    async def delete_file_by_id(self, file_id):
        file_dict = await self.get_file_by_id(file_id)
        file = File.model_validate(file_dict)
        Path(file.path).unlink(missing_ok=True)
        await delete_by_id(file_id, self._collection_name)
