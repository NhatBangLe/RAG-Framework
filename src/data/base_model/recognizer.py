from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from ...config.model.recognizer.image.preprocessing import ImageResizeConfiguration, ImageNormalizeConfiguration, \
    ImageCenterCropConfiguration, ImagePadConfiguration, ImageGrayscaleConfiguration


class OutputClass(BaseModel):
    name: str = Field(description="Name of data class", min_length=1)
    description: str = Field(description="Description for this class, use to search relevant information.",
                             min_length=10, max_length=150)


class ImagePreprocessingType(str, Enum):
    RESIZE = "resize"
    CENTER_CROP = "center_crop"
    PAD = "pad"
    GRAYSCALE = "grayscale"
    NORMALIZE = "normalize"


class ImageResize(ImageResizeConfiguration):
    type: Literal["resize"] = "resize"


class ImageNormalize(ImageNormalizeConfiguration):
    type: Literal["normalize"] = "normalize"


class ImageCenterCrop(ImageCenterCropConfiguration):
    type: Literal["center_crop"] = "center_crop"


class ImagePad(ImagePadConfiguration):
    type: Literal["pad"] = "pad"


class ImageGrayscale(ImageGrayscaleConfiguration):
    type: Literal["grayscale"] = "grayscale"


PreprocessingType = ImageResize | ImageNormalize | ImageCenterCrop | ImagePad | ImageGrayscale


class BaseImageRecognizer(BaseModel):
    name: str = Field(description="Name of the recognizer", min_length=1, max_length=100)
    min_probability: float = Field(default=0.6, ge=0.0, le=1.0)
    max_results: int = Field(default=4, ge=1, le=50)
    output_classes: list[OutputClass] = Field(min_length=1)
    preprocessing: list[PreprocessingType] | None = Field(
        default=None,
        examples=[[
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
        ]])
