from pydantic import Field, BaseModel, field_validator

from ...config.model.chat_model.google_genai import HarmCategory, HarmBlockThreshold, \
    GoogleGenAIChatModelConfiguration
from ...config.model.chat_model.ollama import OllamaChatModelConfiguration


# noinspection PyNestedDecorators
class BaseChatModel(BaseModel):
    model_name: str = Field(min_length=1, max_length=100)

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
