from enum import Enum

from pydantic import BaseModel, Field

from ...config.model.recognizer.image.preprocessing import ImageResizeConfiguration, ImageNormalizeConfiguration, \
    ImageCenterCropConfiguration, ImagePadConfiguration, ImageGrayscaleConfiguration


class ImagePreprocessingType(str, Enum):
    RESIZE = "resize"
    CENTER_CROP = "center_crop"
    PAD = "pad"
    GRAYSCALE = "grayscale"
    NORMALIZE = "normalize"


PreprocessingType = (ImageResizeConfiguration | ImageNormalizeConfiguration
                     | ImageCenterCropConfiguration | ImagePadConfiguration | ImageGrayscaleConfiguration)


class ImagePreprocessing(BaseModel):
    type: ImagePreprocessingType
    config: PreprocessingType


class OutputClass(BaseModel):
    name: str = Field(description="Name of data class", min_length=1)
    description: str = Field(description="Description for this class, use to search relevant information.",
                             min_length=10, max_length=150)


class BaseImageRecognizer(BaseModel):
    min_probability: float = Field(default=0.6, ge=0.0, le=1.0)
    max_results: int = Field(default=4, ge=1, le=50)
    output_classes: list[OutputClass] = Field(min_length=1)
    preprocessing: list[ImagePreprocessing] | None = Field(
        default=None,
        examples=[[
            {
                "type": "resize",
                "config": {
                    "target_size": 256,
                    "interpolation": "bicubic",
                    "max_size": 512,
                    "antialias": True
                }
            },
            {
                "type": "normalize",
                "config": {
                    "mean": [0.485, 0.456, 0.406],
                    "std": [0.229, 0.224, 0.225],
                    "inplace": False
                }
            },
            {
                "type": "center_crop",
                "config": {
                    "size": [64, 64]
                }
            },
            {
                "type": "pad",
                "config": {
                    "padding": 10,
                    "fill": 0,
                    "padding_mode": "constant"
                }
            },
            {
                "type": "grayscale",
                "config": {
                    "num_output_channels": 3
                }
            },
        ]])
