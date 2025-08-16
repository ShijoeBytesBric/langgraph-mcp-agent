LLM_CONFIG = {
    "model": "anthropic:claude-3-7-sonnet-latest",
    "temperature": 0.1,
    "max_tokens": 1000,
}

MCP_SERVERS = {
    "microsoft.docs.mcp": {
        "url": "https://learn.microsoft.com/api/mcp",
        "transport": "streamable_http",
    }
}