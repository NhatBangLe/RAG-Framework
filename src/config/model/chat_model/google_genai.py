from enum import Enum

from pydantic import Field

from src.config.model.chat_model import LLMConfiguration


class HarmCategory(str, Enum):
    UNSPECIFIED = "UNSPECIFIED"
    DEROGATORY = "DEROGATORY"
    TOXICITY = "TOXICITY"
    VIOLENCE = "VIOLENCE"
    SEXUAL = "SEXUAL"
    MEDICAL = "MEDICAL"
    DANGEROUS = "DANGEROUS"
    HARASSMENT = "HARASSMENT"
    HATE_SPEECH = "HATE_SPEECH"
    SEXUALLY_EXPLICIT = "SEXUALLY_EXPLICIT"
    DANGEROUS_CONTENT = "DANGEROUS_CONTENT"
    CIVIC_INTEGRITY = "CIVIC_INTEGRITY"


class HarmBlockThreshold(str, Enum):
    UNSPECIFIED = "UNSPECIFIED"
    BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE"
    BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE"
    BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH"
    BLOCK_NONE = "BLOCK_NONE"
    OFF = "OFF"


class GoogleGenAILLMConfiguration(LLMConfiguration):
    temperature: float = Field(
        description="Run inference with this temperature.", default=0.5, ge=0.0, le=2.0)
    max_tokens: int = Field(
        description="Denotes the number of tokens to predict per generation.",
        default=1024, ge=10)
    max_retries: int = Field(
        description="Number of retries allowed for requests sent to the Anthropic Completion API.",
        default=6, ge=0)
    timeout: float | None = Field(description="Timeout for requests.", default=None, ge=0.0)
    top_k: int | None = Field(
        description="Decode using top-k sampling: consider the set of top_k most probable tokens.",
        default=None, ge=0)
    top_p: float | None = Field(
        description="Decode using nucleus sampling: consider the smallest set of tokens whose probability sum is at least top_p.",
        default=None, ge=0.0, le=1.0)
    safety_settings: dict[str, str] | None = Field(
        default=None,
        description="The default safety settings to use for all generations.")
