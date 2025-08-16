from langchain.chat_models.base import BaseChatModel
from langchain_core.messages import HumanMessage
from langgraph.graph.state import END, StateGraph
from langgraph.prebuilt import ToolNode

from .config import MCP_SERVERS
from .mcp_client import MCPClient
from .schema import AgentState



class Agent:
    def __init__(self, model: BaseChatModel):
        self.model = model
        self.mcp_client = MCPClient(MCP_SERVERS)
        self.agent = None
        self._bound_tools = None
        self._tool_node = None

    async def _get_tools(self, state: AgentState) -> AgentState:
        tools = await self.mcp_client.get_tools()
        return {"tools": tools}
    
    async def _call_model(self, state: AgentState) -> AgentState:
        tools = state.get("tools")
        if tools:
            # Rebind only if tools are different from currently bound ones
            if self._bound_tools != tools:
                self.model = self.model.bind_tools(tools)
                self._bound_tools = tools
                self._tool_node = ToolNode(tools)

        response = await self.model.ainvoke(state["messages"])
        return {"messages": response}
    
    async def _execute_tools(self, state: AgentState) -> AgentState:
        if not self._tool_node:
            return {"messages": []}
        
        last_message = state.get("messages")[-1] if state.get("messages") else None

        if (last_message and hasattr(last_message, 'tool_calls') and last_message.tool_calls):
            tool_results = await self._tool_node.ainvoke(state)
            return {"messages": tool_results["messages"]}
        return {"messages": []}
    
    @staticmethod
    def _should_continue(state: AgentState) -> str:
        if not state.get("messages"):
            return END
        
        last_message = state.get("messages")[-1]

        if (hasattr(last_message, 'tool_calls') and last_message.tool_calls):
            return "execute_tools"
        
        return END
    
    async def build_agent(self):
        agent_flow = StateGraph(AgentState)

        agent_flow.add_node("get_tools", self._get_tools)
        agent_flow.add_node("call_model", self._call_model)
        agent_flow.add_node("execute_tools", self._execute_tools)

        agent_flow.set_entry_point("get_tools")
        agent_flow.add_edge("get_tools", "call_model")
        agent_flow.add_conditional_edges(
            "call_model",
            self._should_continue,
            {
                "execute_tools": "execute_tools",
                END: END
            }
        )
        agent_flow.add_edge("execute_tools", "call_model")
        agent_flow.add_edge("call_model", END)

        agent = agent_flow.compile()
        return agent
    
    async def run (self, question: str):
        if not self.agent:
            self.agent = await self.build_agent()
        response = await self.agent.ainvoke({"messages": HumanMessage(content=question)})
        return response
