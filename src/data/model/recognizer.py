from pydantic import Field, ConfigDict

from src.config.model.recognizer.image import ImageRecognizerConfiguration
from src.data import PyObjectId


class ImageRecognizer(ImageRecognizerConfiguration):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
