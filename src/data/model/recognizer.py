from pydantic import Field, ConfigDict

from ...data import PyObjectId
from ...data.base_model.recognizer import BaseImageRecognizer


class ImageRecognizer(BaseImageRecognizer):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
