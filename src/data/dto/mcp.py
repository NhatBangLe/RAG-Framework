from pydantic import Field, ConfigDict

from ..base_model import BaseMCP
from ...data import PyObjectId


class MCPCreate(BaseMCP):
    pass


class MCPUpdate(BaseMCP):
    pass


class MCPPublic(BaseMCP):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
