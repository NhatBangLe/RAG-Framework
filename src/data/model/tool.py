from pydantic import Field, ConfigDict

from .. import PyObjectId
from ..base_model.tool import BaseDuckDuckGoSearchTool


class DuckDuckGoSearchTool(BaseDuckDuckGoSearchTool):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


Tool = DuckDuckGoSearchTool
