from enum import Enum

from pydantic import Field, BaseModel, field_validator

from ...config.model.chat_model.google_genai import HarmCategory, HarmBlockThreshold, GoogleGenAILLMConfiguration
from ...config.model.chat_model.ollama import OllamaLLMConfiguration


class ChatModelType(str, Enum):
    GOOGLE_GENAI = "google_genai"
    OLLAMA = "ollama"


# noinspection PyNestedDecorators
class BaseChatModel(BaseModel):
    type: ChatModelType = Field(description="Type of the chat model.", frozen=True)
    model_name: str = Field(min_length=1, max_length=100)

    @field_validator("model_name", mode="after")
    @classmethod
    def validate_model_name(cls, model_name: str):
        if len(model_name.strip()) == 0:
            raise ValueError(f'model_name cannot be blank.')
        return model_name


class BaseGoogleGenAIChatModel(BaseChatModel, GoogleGenAILLMConfiguration):
    type: ChatModelType = ChatModelType.GOOGLE_GENAI
    safety_settings: dict[HarmCategory, HarmBlockThreshold] | None = Field(
        default=None,
        description="The default safety settings to use for all generations.")


class BaseOllamaChatModel(BaseChatModel, OllamaLLMConfiguration):
    type: ChatModelType = ChatModelType.OLLAMA
