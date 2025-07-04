from pydantic import BaseModel, Field


class BasePrompt(BaseModel):
    suggest_questions_prompt: str = Field(min_length=8)
    respond_prompt: str = Field(min_length=11)
