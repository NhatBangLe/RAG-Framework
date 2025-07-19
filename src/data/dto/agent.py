from pydantic import Field, ConfigDict

from .. import PyObjectId
from ..base_model import BaseAgent



class AgentCreate(BaseAgent):
    pass


class AgentUpdate(BaseAgent):
    pass


class AgentPublic(BaseAgent):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
