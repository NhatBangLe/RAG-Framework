from pydantic import Field, ConfigDict

from .. import PyObjectId
from ...config.model.recognizer.image import ImageRecognizerConfiguration
from ...data.base_model.recognizer import BaseImageRecognizer


class ImageRecognizerCreate(BaseImageRecognizer):
    pass


class ImageRecognizerUpdate(BaseImageRecognizer):
    pass


class ImageRecognizerPublic(ImageRecognizerConfiguration):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
