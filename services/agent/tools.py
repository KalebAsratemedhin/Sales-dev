from langchain_core.tools import tool

@tool
def no_op_tool(query: str) -> str:
    return query