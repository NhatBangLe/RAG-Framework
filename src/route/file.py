import asyncio
import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, status, UploadFile

from ..data.database import MongoCollection, get_by_id, delete_by_id, create_document
from ..data.dto import FilePublic
from ..data.model import File
from ..util.constant import EnvVar

router = APIRouter(
    prefix="/api/v1/file",
    tags=["File"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)


@router.get(
    path="/{file_id}/metadata",
    response_model=FilePublic,
    description="Get a file by its ID.",
    status_code=status.HTTP_200_OK)
async def get_file_by_id(file_id: str):
    not_found_msg = f'No file with id {file_id} found.'
    return await get_by_id(file_id, MongoCollection.FILE, not_found_msg)


@router.post(
    path="/upload",
    description="Upload a file. Returns an ID of the uploaded file.",
    status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile) -> str:
    save_path = Path(os.getenv(EnvVar.LOCAL_FILE_DIR.value, "/app/local"), str(uuid4()))
    file_record = File(name=file.filename, mime_type=file.content_type, path=str(save_path))
    async with asyncio.TaskGroup() as tg:
        content_task = tg.create_task(file.read())
        save_record_task = tg.create_task(create_document(file_record, MongoCollection.FILE))
    save_path.write_bytes(content_task.result())
    return save_record_task.result()


@router.delete(
    path="/{file_id}",
    description="Delete a file.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: str) -> None:
    await delete_by_id(file_id, MongoCollection.FILE)
