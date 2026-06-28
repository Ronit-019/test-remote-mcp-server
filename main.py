from fastmcp import FastMCP
import random
import json

mcp = FastMCP("Simple Calculator Server")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers
        Args: 
            a: first number
            b: second number
        Return:
            sum of a and b
    """
    
    return a+b

@mcp.tool
def random_number(min_val: int=1, max_val: int=100) -> int:
    """Generate Random number within a range.
    Args:
        min_val: Minimum value(default=1)
        max_val: Maximimum value(default=100)

    Returns:
        A random integer between min_val and max_val
    """
    return random.randint(min_val, max_val)

@mcp.tool
def server_info() -> str:
    """Get information about the server."""
    info={
        "name": "Simple Calculator Example",
        "version" : "1.0.0",
        "description" : "A basic MCP server with math tools.",
        "tools" : ["add","random_number"],
        "author" : "Ronit Rajput"
    }
    return json.dumps(info, indent=2)

if __name__ == "__main__":

    mcp.run(transport="http", host="0.0.0.0", port=8000)
    