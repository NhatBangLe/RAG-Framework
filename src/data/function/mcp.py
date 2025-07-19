from ..database import get_by_id, MongoCollection, update_by_id, delete_by_id, get_collection, create_document
from ..dto.mcp import MCPUpdate, MCPPublic, MCPCreate
from ..model import MCP
from ...config.model.mcp import MCPConfiguration, MCPConnectionConfiguration
from ...util import PagingWrapper, PagingParams


async def get_all_mcp_entities_as_documents(params: PagingParams) -> PagingWrapper[MCPPublic]:
    collection = get_collection(MongoCollection.PROMPT)
    return await PagingWrapper.get_paging(params, collection)


async def get_mcp_as_document(model_id: str):
    not_found_msg = f'No MCP configuration with id {model_id} found.'
    return await get_by_id(model_id, MongoCollection.MCP, not_found_msg)


async def get_mcp_as_configuration(mcp_id: str) -> MCPConfiguration:
    doc_mcp = await get_mcp_as_document(mcp_id)
    mcp = MCP.model_validate(doc_mcp)
    connections: dict[str, MCPConnectionConfiguration] = {}
    for server in mcp.servers:
        connections[server.name] = MCPConnectionConfiguration.model_validate(server.model_dump())
    return MCPConfiguration.model_validate({connections})


async def create_mcp_as_document(data: MCPCreate):
    model = MCP.model_validate(data.model_dump())
    return await create_document(model, MongoCollection.MCP)


async def update_mcp_as_document(model_id: str, data: MCPUpdate):
    not_found_msg = f'Cannot update MCP configuration with id {model_id}. Because no MCP configuration found.'
    model = MCP.model_validate(data.model_dump())
    await update_by_id(model_id, model, MongoCollection.MCP, not_found_msg)


async def delete_mcp_by_id(mcp_id: str):
    await delete_by_id(mcp_id, MongoCollection.MCP)
