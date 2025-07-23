from pydantic import Field, ConfigDict

from ...data import PyObjectId
from ...data.base_model import BasePrompt


class PromptCreate(BasePrompt):
    pass


class PromptUpdate(BasePrompt):
    pass


class PromptPublic(BasePrompt):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
