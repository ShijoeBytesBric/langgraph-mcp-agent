from langchain.tools.base import BaseTool


class StateReducers:

    @staticmethod
    def replace_tools(old: BaseTool, new: BaseTool) -> BaseTool:
        return new