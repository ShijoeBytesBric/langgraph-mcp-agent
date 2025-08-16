from typing import Annotated, TypedDict, List

from langgraph.graph.message import add_messages
from .state_reducers import StateReducers

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    tools: Annotated[List, StateReducers.replace_tools]