from pydantic import Field, ConfigDict

from .. import PyObjectId
from ..base_model import BaseFile


class FilePublic(BaseFile):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    path: str = Field(exclude=True)
