from pydantic import Field, ConfigDict

from ..base_model import BaseMCPStreamableServer, BaseMCPStdioServer
from ...data import PyObjectId


class MCPStreamableServerCreate(BaseMCPStreamableServer):
    pass


class MCPStreamableServerUpdate(BaseMCPStreamableServer):
    pass


class MCPStreamableServerPublic(BaseMCPStreamableServer):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MCPStdioServerCreate(BaseMCPStdioServer):
    pass


class MCPStdioServerUpdate(BaseMCPStdioServer):
    pass


class MCPStdioServerPublic(BaseMCPStdioServer):
    id: PyObjectId = Field(validation_alias="_id")
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


MCPCreate = MCPStreamableServerCreate | MCPStdioServerCreate
MCPUpdate = MCPStreamableServerUpdate | MCPStdioServerUpdate
MCPPublic = MCPStreamableServerPublic | MCPStdioServerPublic
