from pydantic import BaseModel, Field

from ...config.model.tool.search import SearchToolType


class BaseTool(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class SearchTool(BaseTool):
    type: SearchToolType = Field(description="Search engine type.")
    max_results: int = Field(description="Max results return from Search engine.", ge=1, default=4)


class BaseDuckDuckGoSearchTool(SearchTool):
    type: SearchToolType = Field(default=SearchToolType.DUCKDUCKGO_SEARCH, frozen=True)
