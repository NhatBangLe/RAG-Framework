from typing import Annotated

from fastapi import APIRouter, status, Body

from ..data.base_model.recognizer import BaseRecognizer, RecognizerType
from ..data.database import get_collection, MongoCollection, get_by_id, delete_by_id, update_by_id, create_document
from ..data.dto.recognizer import ImageRecognizerCreate, ImageRecognizerUpdate, RecognizerPublic
from ..data.model.recognizer import ImageRecognizer
from ..dependency import PagingQuery
from ..util import PagingWrapper
from ..util.error import InvalidArgumentError


async def get_document(recognizer_id: str):
    not_found_msg = f'No recognizer with id {recognizer_id} found.'
    return await get_by_id(recognizer_id, MongoCollection.EMBEDDINGS, not_found_msg)


def get_model(base_data: BaseRecognizer):
    if base_data.type == RecognizerType.IMAGE:
        return ImageRecognizer.model_validate(base_data.model_dump())
    else:
        raise InvalidArgumentError(f'Retriever type {base_data.type} is not supported.')


async def update_document(recognizer_id: str, model: BaseRecognizer):
    not_found_msg = f'Cannot update recognizer with id {recognizer_id}. Because no recognizer found.'
    await update_by_id(recognizer_id, model, MongoCollection.EMBEDDINGS, not_found_msg)


router = APIRouter(
    prefix="/api/v1/recognizer",
    tags=["Recognizer"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

ImageRecognizerCreateBody = Annotated[ImageRecognizerCreate, Body(
    example={
        "name": "YOLOv11-cls",
        "model_file_id": "686003f271e4995bcb0c2d0f",
        "min_probability": 0.75,
        "max_results": 5,
        "output_classes": [
            {
                "name": "Product",
                "description": "Represents a retail product with attributes like price, inventory, and category. Used for e-commerce applications."
            },
            {
                "name": "CustomerReview",
                "description": "Contains feedback and ratings submitted by customers for products or services. Includes text and star ratings."
            },
            {
                "name": "BlogPost",
                "description": "Defines a single entry in a blog, including its title, content, author, and publication date. Used for content management systems."
            }
        ],
        "preprocessing": [
            {
                "type": "resize",
                "target_size": 256,
                "interpolation": "bicubic",
                "max_size": 512,
                "antialias": True
            },
            {
                "type": "normalize",
                "mean": [0.485, 0.456, 0.406],
                "std": [0.229, 0.224, 0.225],
                "inplace": False
            },
            {
                "type": "center_crop",
                "size": [64, 64]
            },
            {
                "type": "pad",
                "padding": 10,
                "fill": 0,
                "padding_mode": "constant"
            },
            {
                "type": "grayscale",
                "num_output_channels": 3
            },
        ],
    }
)]
ImageRecognizerUpdateBody = Annotated[ImageRecognizerUpdate, Body(
    example={
        "name": "YOLOv8-cls",
        "min_probability": 0.75,
        "max_results": 5,
        "output_classes": [
            {
                "name": "Product",
                "description": "Represents a retail product with attributes like price, inventory, and category. Used for e-commerce applications."
            },
            {
                "name": "CustomerReview",
                "description": "Contains feedback and ratings submitted by customers for products or services. Includes text and star ratings."
            },
        ],
        "preprocessing": [
            {
                "type": "resize",
                "target_size": 256,
                "interpolation": "bicubic",
                "max_size": 512,
                "antialias": True
            },
            {
                "type": "center_crop",
                "size": [64, 64]
            },
            {
                "type": "pad",
                "padding": 10,
                "fill": 0,
                "padding_mode": "constant"
            },
            {
                "type": "grayscale",
                "num_output_channels": 3
            },
        ],
    }
)]


@router.get(
    path="/all",
    response_model=PagingWrapper,
    description="Get all recognizers.",
    status_code=status.HTTP_200_OK)
async def get_all(params: PagingQuery):
    collection = get_collection(MongoCollection.RECOGNIZER)
    return await PagingWrapper.get_paging(params, collection)


@router.get(
    path="/{recognizer_id}",
    response_model=RecognizerPublic,
    description="Get a recognizer by its ID.",
    status_code=status.HTTP_200_OK)
async def get_image_recognizer(recognizer_id: str):
    return await get_document(recognizer_id)


@router.post(
    path="/create",
    description="Create a recognizer.",
    status_code=status.HTTP_200_OK)
async def create_image_recognizer(body: ImageRecognizerCreateBody) -> str:
    model = ImageRecognizer.model_validate(body.model_dump())
    return await create_document(model, MongoCollection.RECOGNIZER)


@router.put(
    path="/{recognizer_id}/update",
    description="Update a recognizer.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_image_recognizer(recognizer_id: str, body: ImageRecognizerUpdateBody) -> None:
    await update_document(recognizer_id, body)


@router.delete(
    path="/{recognizer_id}",
    description="Delete a recognizer.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete(recognizer_id: str) -> None:
    await delete_by_id(recognizer_id, MongoCollection.RECOGNIZER)
