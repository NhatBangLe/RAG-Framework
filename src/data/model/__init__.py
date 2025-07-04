from pydantic import Field, ConfigDict

from src.config.model.agent import AgentConfiguration
from src.config.model.prompt import PromptConfiguration
from src.data import PyObjectId


class Agent(AgentConfiguration):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class Prompt(PromptConfiguration):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
