# MCP Agent

A Python-based intelligent agent that leverages the Model Context Protocol (MCP) to interact with external services and provide enhanced AI capabilities through LangChain and LangGraph.

## Overview

This project implements an AI agent that can dynamically connect to MCP servers to access external tools and resources. The agent uses LangChain for language model integration and LangGraph for workflow orchestration, creating a flexible and extensible AI assistant.

## Features

- **MCP Integration**: Connects to multiple MCP servers to access external tools and APIs
- **Dynamic Tool Binding**: Automatically discovers and binds tools from connected MCP servers
- **Interactive Chat Interface**: Provides a user-friendly command-line chat experience
- **Conversation History**: Maintains chat history with configurable limits
- **Async Support**: Built with async/await for efficient concurrent operations
- **Configurable Models**: Support for different language models (currently configured for Anthropic Claude)
- **State Management**: Uses LangGraph for sophisticated agent state management

## Architecture

The project is structured around several key components:

- **Agent**: Core agent class that orchestrates the workflow
- **MCP Client**: Handles connections to MCP servers and tool discovery
- **LLM Provider**: Manages language model configuration and initialization
- **Interactive Chat**: Provides a conversational interface for users
- **State Management**: Handles agent state transitions and message flow

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mcp_agent
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory with your API keys:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Configuration

### MCP Servers

Configure MCP servers in `src/mcp_agent/config.py`:

```python
MCP_SERVERS = {
    "microsoft.docs.mcp": {
        "url": "https://learn.microsoft.com/api/mcp",
        "transport": "streamable_http",
    }
    # Add more MCP servers as needed
}
```

### Language Model

Configure the language model settings in `src/mcp_agent/config.py`:

```python
LLM_CONFIG = {
    "model": "anthropic:claude-3-7-sonnet-latest",
    "temperature": 0.1,
    "max_tokens": 1000,
}
```

## Usage

### Interactive Chat

Start an interactive chat session:

```bash
uv run interactive_chat.py
```

This provides a command-line interface where you can:
- Chat with the agent
- View conversation history with `history`
- Clear history with `clear`
- Get agent information with `info`
- Exit with `quit`, `exit`, or `bye`

### Programmatic Usage

Use the agent programmatically:

```python
import asyncio
from dotenv import load_dotenv
from src.mcp_agent import Agent, LLMProvider

load_dotenv()

async def main():
    llm = LLMProvider().model
    agent = Agent(llm)
    
    response = await agent.run("Your question here")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Simple Example

Run the basic example:

```bash
uv run main.py
```

This will ask the agent about Office 365 updates and save the response to `response.txt`.

## Project Structure

```
mcp_agent/
├── src/
│   └── mcp_agent/
│       ├── __init__.py          # Package initialization
│       ├── agent.py             # Core agent implementation
│       ├── config.py            # Configuration settings
│       ├── llm_provider.py      # Language model provider
│       ├── mcp_client.py        # MCP client wrapper
│       ├── schema.py            # Data schemas and types
│       └── state_reducers.py    # State management utilities
├── interactive_chat.py          # Interactive chat interface
├── main.py                      # Basic usage example
├── pyproject.toml              # Project configuration
├── .env                        # Environment variables (create this)
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Dependencies

- **langchain**: Core LangChain framework for LLM integration
- **langchain-anthropic**: Anthropic Claude model integration
- **langchain-mcp-adapters**: MCP protocol adapters for LangChain
- **langgraph**: Graph-based workflow orchestration
- **python-dotenv**: Environment variable management

## How It Works

1. **Initialization**: The agent initializes with a language model and MCP client
2. **Tool Discovery**: Connects to configured MCP servers and discovers available tools
3. **Dynamic Binding**: Binds discovered tools to the language model
4. **Workflow Execution**: Uses LangGraph to manage the conversation flow:
   - Get available tools from MCP servers
   - Call the language model with user input and available tools
   - Execute any tool calls requested by the model
   - Return the final response to the user

## Extending the Agent

### Adding New MCP Servers

1. Add server configuration to `MCP_SERVERS` in `config.py`
2. The agent will automatically discover and use tools from the new server

### Custom Tool Integration

The agent automatically integrates tools from MCP servers. To add custom functionality:

1. Create or configure an MCP server with your custom tools
2. Add the server to the configuration
3. The agent will automatically discover and use the new tools

## Development

### Requirements

- Python 3.13+
- Anthropic API key (for Claude models)
