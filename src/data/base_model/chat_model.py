from enum import Enum

from pydantic import Field

from ...config.model.chat_model import LLMConfiguration
from ...config.model.chat_model.google_genai import HarmCategory, HarmBlockThreshold, GoogleGenAILLMConfiguration
from ...config.model.chat_model.ollama import OllamaLLMConfiguration


class ChatModelType(str, Enum):
    GOOGLE_GENAI = "google_genai"
    OLLAMA = "ollama"


class BaseChatModel(LLMConfiguration):
    type: ChatModelType = Field(description="Type of the chat model.", frozen=True)


class BaseGoogleGenAIChatModel(BaseChatModel, GoogleGenAILLMConfiguration):
    type: ChatModelType = ChatModelType.GOOGLE_GENAI
    safety_settings: dict[HarmCategory, HarmBlockThreshold] | None = Field(
        default=None,
        description="The default safety settings to use for all generations.")


class BaseOllamaChatModel(BaseChatModel, OllamaLLMConfiguration):
    type: ChatModelType = ChatModelType.OLLAMA
