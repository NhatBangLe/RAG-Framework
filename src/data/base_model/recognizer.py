from enum import Enum

from pydantic import BaseModel, Field, field_validator

from ...config.model.recognizer.image.preprocessing import ImageResizeConfiguration, ImagePadConfiguration, \
    ImageGrayscaleConfiguration


class RecognizerType(str, Enum):
    IMAGE = "image"


# noinspection PyNestedDecorators
class BaseRecognizer(BaseModel):
    name: str = Field(description="Name of the recognizer", min_length=1, max_length=100)
    type: RecognizerType = Field(description="Type of the recognizer.", frozen=True)
    model_file_id: str = Field(min_length=1)
    min_probability: float = Field(description="A low probability limit for specifying classes.", ge=0.0, le=1.0)
    max_results: int = Field(description="The maximum number of results recognized is used for prompting.",
                             default=4, ge=1, le=50)

    @field_validator("name", mode="after")
    @classmethod
    def validate_name(cls, name: str):
        if len(name.strip()) == 0:
            raise ValueError(f'name cannot be blank.')
        return name


class OutputClass(BaseModel):
    name: str = Field(description="Name of data class", min_length=1)
    description: str = Field(description="Description for this class, use to search relevant information.",
                             min_length=10, max_length=150)


class ImagePreprocessingType(str, Enum):
    RESIZE = "resize"
    PAD = "pad"
    GRAYSCALE = "grayscale"


class BaseImagePreprocessing(BaseModel):
    type: ImagePreprocessingType = Field(description="Type of the preprocessing.", frozen=True)


class ImageResize(BaseImagePreprocessing, ImageResizeConfiguration):
    type: ImagePreprocessingType = ImagePreprocessingType.RESIZE


class ImagePad(BaseImagePreprocessing, ImagePadConfiguration):
    type: ImagePreprocessingType = ImagePreprocessingType.PAD


class ImageGrayscale(BaseImagePreprocessing, ImageGrayscaleConfiguration):
    type: ImagePreprocessingType = ImagePreprocessingType.GRAYSCALE


PreprocessingType = ImageResize | ImagePad | ImageGrayscale


class BaseImageRecognizer(BaseRecognizer):
    type: RecognizerType = RecognizerType.IMAGE
    output_classes: list[OutputClass] = Field(min_length=1)
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
