from enum import Enum

from pydantic import Field
from src.config.model import Configuration

__all__ = ["anthropic", "google_genai", "ollama", "LLMConfiguration"]


class LLMConfiguration(Configuration):
    """
    An interface for large language model configuration classes
    """
    model_name: str = Field(min_length=1)


class LLMProvider(Enum):
    GOOGLE_GENAI = "google_genai"
