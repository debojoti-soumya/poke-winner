#!/usr/bin/env python3
import os
import json
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Browser History MCP Server")

@mcp.tool(description="Get browser history from stored file")
def get_browser_history() -> list:
    """Get all stored browser history from the history file"""
    try:
        # Use absolute path to ensure both servers use the same file
        history_file = "/tmp/browser_history.txt"
        
        if not os.path.exists(history_file):
            return []
        
        history_data = []
        with open(history_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    history_data.append(json.loads(line))
        
        print(f"Retrieved {len(history_data)} browser history items")
        return history_data
        
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading browser history file: {e}")
        return []

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting Browser History MCP Server on {host}:{port}")
    print(f"MCP endpoint: http://{host}:{port}/mcp")
    print("Available tools:")
    print("- get_browser_history() - Get all stored browser history")
    
    mcp.run(
        transport="http",
        host=host,
        port=port
    )