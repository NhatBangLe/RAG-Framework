from enum import Enum

from pydantic import BaseModel, Field

from ...config.model.recognizer import RecognizerConfiguration
from ...config.model.recognizer.image import ImageRecognizerConfiguration
from ...config.model.recognizer.image.preprocessing import ImageResizeConfiguration, ImageNormalizeConfiguration, \
    ImageCenterCropConfiguration, ImagePadConfiguration, ImageGrayscaleConfiguration


class RecognizerType(str, Enum):
    IMAGE = "image"


class BaseRecognizer(RecognizerConfiguration):
    name: str = Field(description="Name of the recognizer", min_length=1, max_length=100)
    type: RecognizerType = Field(description="Type of the recognizer.", frozen=True)


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


class BaseImagePreprocessing(BaseModel):
    type: ImagePreprocessingType = Field(description="Type of the preprocessing.", frozen=True)


class ImageResize(BaseImagePreprocessing, ImageResizeConfiguration):
    type: ImagePreprocessingType = ImagePreprocessingType.RESIZE


class ImageNormalize(BaseImagePreprocessing, ImageNormalizeConfiguration):
    type: ImagePreprocessingType = ImagePreprocessingType.NORMALIZE


class ImageCenterCrop(BaseImagePreprocessing, ImageCenterCropConfiguration):
    type: ImagePreprocessingType = ImagePreprocessingType.CENTER_CROP


class ImagePad(BaseImagePreprocessing, ImagePadConfiguration):
    type: ImagePreprocessingType = ImagePreprocessingType.PAD


class ImageGrayscale(BaseImagePreprocessing, ImageGrayscaleConfiguration):
    type: ImagePreprocessingType = ImagePreprocessingType.GRAYSCALE


PreprocessingType = ImageResize | ImageNormalize | ImageCenterCrop | ImagePad | ImageGrayscale


class BaseImageRecognizer(BaseRecognizer, ImageRecognizerConfiguration):
    type: RecognizerType = RecognizerType.IMAGE
    output_classes: list[OutputClass] = Field(min_length=1)
    model_file_id: str = Field(min_length=1)
    preprocessing_configs: list[PreprocessingType] | None = Field(
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

    # Exclude fields
    enable: bool = Field(default=True, exclude=True)
    path: str | None = Field(default=None, exclude=True)
    output_config_path: str | None = Field(default=None, exclude=True)
    device: str | None = Field(default=None, exclude=True)
    preprocessing: list | None = Field(default=None)
