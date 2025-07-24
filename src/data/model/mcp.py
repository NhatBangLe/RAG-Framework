from pydantic import Field, ConfigDict

from .. import PyObjectId
from ..base_model import BaseMCPStreamableServer, BaseMCPStdioServer


class MCPStreamableServer(BaseMCPStreamableServer):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MCPStdioServer(BaseMCPStdioServer):
    id: PyObjectId | None = Field(alias="_id", exclude=True, default=None)
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


MCP = MCPStreamableServer | MCPStdioServer
