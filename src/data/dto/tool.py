from pydantic import Field, ConfigDict

from .. import PyObjectId
from ..base_model.tool import BaseDuckDuckGoSearchTool


class DuckDuckGoSearchToolCreate(BaseDuckDuckGoSearchTool):
    pass


class DuckDuckGoSearchToolUpdate(BaseDuckDuckGoSearchTool):
    pass


class DuckDuckGoSearchToolPublic(BaseDuckDuckGoSearchTool):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


ToolCreate = DuckDuckGoSearchToolCreate
ToolUpdate = DuckDuckGoSearchToolUpdate
ToolPublic = DuckDuckGoSearchToolPublic
