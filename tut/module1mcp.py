'''
# Creates mcp server
from mcp.server import FastMCP

mcp = FastMCP("Calculator Server")

@mcp.tool(description="Add two numbers together")
def add(x: int, y: int) -> int:
    """Add two numbers and return the result."""
    return x + y

mcp.run(transport="streamable-http")
'''

# Creates mcp server
from mcp.server import FastMCP

mcp = FastMCP("test")

@mcp.tool(description="multiply")
def add(x: int, y: int) -> int:
    """multiply two numbers and return the result, append an encouraging message."""
    return x + y

mcp.run(transport="streamable-http")

