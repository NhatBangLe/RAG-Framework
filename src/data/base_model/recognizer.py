from enum import Enum

from pydantic import BaseModel, Field

from ...config.model.recognizer.image.preprocessing import ImageResizeConfiguration, ImageNormalizeConfiguration, \
    ImageCenterCropConfiguration, ImagePadConfiguration, ImageGrayscaleConfiguration


class ImagePreprocessingType(str, Enum):
    RESIZE = "resize"
    CROP = "crop"
    PAD = "pad"
    GRAYSCALE = "grayscale"
    NORMALIZE = "normalize"


PreprocessingType = (ImageResizeConfiguration | ImageNormalizeConfiguration
                     | ImageCenterCropConfiguration | ImagePadConfiguration | ImageGrayscaleConfiguration)


class BaseImageRecognizer(BaseModel):
    preprocessing: list[PreprocessingType] | None = Field(
        default=None,
        examples=[{
            "target_size": 256,
            "interpolation": "bicubic",
            "max_size": 512,
            "antialias": True
        }])
    min_probability: float = Field(default=0.6, ge=0.0, le=1.0)
    max_results: int = Field(default=4, ge=1, le=50)
