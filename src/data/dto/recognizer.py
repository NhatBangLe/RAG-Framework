from pydantic import Field, ConfigDict

from .. import PyObjectId
from ...data.base_model.recognizer import BaseImageRecognizer


class ImageRecognizerCreate(BaseImageRecognizer):
    model_file_id: str = Field(min_length=1)


class ImageRecognizerUpdate(BaseImageRecognizer):
    pass


class ImageRecognizerPublic(BaseImageRecognizer):
    id: PyObjectId = Field(validation_alias="_id")
    model_file_id: str = Field(min_length=1)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
