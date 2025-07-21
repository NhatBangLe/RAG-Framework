from typing import Annotated

from fastapi import APIRouter, status, Body

from ..data.dto.recognizer import RecognizerPublic, RecognizerCreate, \
    RecognizerUpdate
from ..dependency import PagingQuery, RecognizerServiceDepend
from ..util import PagingWrapper

router = APIRouter(
    prefix="/api/v1/recognizer",
    tags=["Recognizer"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)

RecognizerCreateBody = Annotated[RecognizerCreate, Body(
    examples=[
        {
            "name": "YOLOv11-cls",
            "type": "image",
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
    ]
)]
RecognizerUpdateBody = Annotated[RecognizerUpdate, Body(
    examples=[
        {
            "name": "YOLOv8-cls",
            "type": "image",
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
    ]
)]


@router.get(
    path="/all",
    response_model=PagingWrapper,
    description="Get all recognizers.",
    status_code=status.HTTP_200_OK)
async def get_all(params: PagingQuery, service: RecognizerServiceDepend):
    return await service.get_all_models_with_paging(params, True)


@router.get(
    path="/{recognizer_id}",
    response_model=RecognizerPublic,
    description="Get a recognizer by its ID.",
    status_code=status.HTTP_200_OK)
async def get_recognizer(recognizer_id: str, service: RecognizerServiceDepend):
    return await service.get_model_by_id(recognizer_id)


@router.post(
    path="/create",
    description="Create a recognizer.",
    status_code=status.HTTP_200_OK)
async def create_recognizer(body: RecognizerCreateBody, service: RecognizerServiceDepend) -> str:
    return await service.create_new(body)


@router.put(
    path="/{recognizer_id}/update",
    description="Update a recognizer.",
    status_code=status.HTTP_204_NO_CONTENT)
async def update_recognizer(recognizer_id: str, body: RecognizerUpdateBody, service: RecognizerServiceDepend) -> None:
    await service.update_model_by_id(recognizer_id, body)


@router.delete(
    path="/{recognizer_id}",
    description="Delete a recognizer.",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_recognizer(recognizer_id: str, service: RecognizerServiceDepend) -> None:
    await service.delete_model_by_id(recognizer_id)
