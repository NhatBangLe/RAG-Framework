from fastapi import APIRouter, status, UploadFile

from ..data.dto import FilePublic
from ..dependency import FileServiceDepend

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
async def get_file_metadata(file_id: str, service: FileServiceDepend):
    return await service.get_file_by_id(file_id)


@router.post(
    path="/upload",
    description="Upload a file. Returns an ID of the uploaded file.",
    status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile, service: FileServiceDepend) -> str:
    return await service.save_file(file)


@router.delete(
    path="/{file_id}",
    description="Delete a file.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: str, service: FileServiceDepend) -> None:
    await service.delete_file_by_id(file_id)
