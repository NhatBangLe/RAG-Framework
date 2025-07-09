from pydantic import Field, ConfigDict

from ...data import PyObjectId
from ...data.base_model.chat_model import BaseGoogleGenAIChatModel, BaseOllamaChatModel


class GoogleGenAIChatModelCreate(BaseGoogleGenAIChatModel):
    pass


class GoogleGenAIChatModelUpdate(BaseGoogleGenAIChatModel):
    pass


class GoogleGenAIChatModelPublic(BaseGoogleGenAIChatModel):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class OllamaChatModelCreate(BaseOllamaChatModel):
    pass


class OllamaChatModelUpdate(BaseOllamaChatModel):
    pass


class OllamaChatModelPublic(BaseOllamaChatModel):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


ChatModelCreate = GoogleGenAIChatModelCreate | OllamaChatModelCreate
ChatModelUpdate = GoogleGenAIChatModelUpdate | OllamaChatModelUpdate
ChatModelPublic = GoogleGenAIChatModelPublic | OllamaChatModelPublic
