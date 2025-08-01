from pydantic import Field, BaseModel, field_validator

from ...config.model.chat_model.google_genai import HarmCategory, HarmBlockThreshold, \
    GoogleGenAIChatModelConfiguration
from ...config.model.chat_model.ollama import OllamaChatModelConfiguration


# noinspection PyNestedDecorators
class BaseChatModel(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    model_name: str = Field(min_length=1, max_length=100)

    @field_validator("name", mode="after")
    @classmethod
    def validate_name(cls, name: str):
        if len(name.strip()) == 0:
            raise ValueError(f'name cannot be blank.')
        return name

    @field_validator("model_name", mode="after")
    @classmethod
    def validate_model_name(cls, model_name: str):
        if len(model_name.strip()) == 0:
            raise ValueError(f'model_name cannot be blank.')
        return model_name


class BaseGoogleGenAIChatModel(BaseChatModel, GoogleGenAIChatModelConfiguration):
    safety_settings: dict[HarmCategory, HarmBlockThreshold] | None = Field(
        default=None,
        description="The default safety settings to use for all generations.")


class BaseOllamaChatModel(BaseChatModel, OllamaChatModelConfiguration):
    pass
