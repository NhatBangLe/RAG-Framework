from pydantic import Field, ConfigDict

from .. import PyObjectId
from ...data.base_model.recognizer import BaseImageRecognizer


class ImageRecognizerCreate(BaseImageRecognizer):
    pass


class ImageRecognizerUpdate(BaseImageRecognizer):
    pass


class ImageRecognizerPublic(BaseImageRecognizer):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


RecognizerCreate = ImageRecognizerCreate
RecognizerUpdate = ImageRecognizerUpdate
RecognizerPublic = ImageRecognizerPublic
