import os

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("File & Calculator")


@mcp.tool()
def read_file(path: str) -> str:
    """Read a text file from the local filesystem."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except PermissionError:
        return f"Error: permission denied: {path}"
    except IsADirectoryError:
        return f"Error: is a directory: {path}"


@mcp.tool()
def calculate(a: float, b: float, operation: str) -> float:
    """Perform a basic arithmetic operation."""
    if operation == "add":
        return a + b
    if operation == "subtract":
        return a - b
    if operation == "multiply":
        return a * b
    if operation == "divide":
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    raise ValueError(f"Unsupported operation: {operation}")


if __name__ == "__main__":
    port = int(os.environ.get("MCP_SERVER_PORT", "8001"))
    mcp.settings.port = port
    mcp.run(transport="sse")
