from langchain_mcp_adapters.client import MultiServerMCPClient

class MCPClient:
    def __init__(self, mcp_servers: list[str]):
        self.mcp_client = MultiServerMCPClient(mcp_servers)

    async def get_tools(self):
        return await self.mcp_client.get_tools()
