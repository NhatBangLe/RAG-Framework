from pydantic import Field, ConfigDict

from .. import PyObjectId
from ..base_model.chat_model import BaseGoogleGenAIChatModel, BaseOllamaChatModel


class GoogleGenAIChatModel(BaseGoogleGenAIChatModel):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class OllamaChatModel(BaseOllamaChatModel):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
