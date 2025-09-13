#!/usr/bin/env python3
import os
import json
from fastmcp import FastMCP
from birthday import generate_birthday_prompt
# Initialize FastMCP server
mcp = FastMCP("History MCP Server")

# Global variables to store history data
history = []
read = set()

@mcp.tool(description="Greet a user by name with a welcome message from the MCP server")
def greet(name: str) -> str:
    return f"Hello, {name}! Welcome to our History MCP server running on Render!"

@mcp.tool(description="Get information about the MCP server including name, version, environment, and Python version")
def get_server_info() -> dict:
    return {
        "server_name": "History MCP Server",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": os.sys.version.split()[0]
    }

@mcp.tool(description="Get all stored browser history data")
def get_search_history() -> list:
    """Get all stored browser history data"""
    try:
        file_data = []
        history_file = os.path.join(os.path.dirname(__file__), "history.txt")
        
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:  # Skip empty lines
                        file_data.append(json.loads(line))
        
        print(f"Retrieved {len(file_data)} history items from file")
        return file_data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading history file: {e}")
        return []

@mcp.tool(description="Store browser history data from Chrome extension")
def store_history_data(history_data: list) -> dict:
    """Store browser history data from Chrome extension"""
    global history, read
    
    if not history_data:
        return {"status": "error", "message": "No history data provided"}
    
    stored_count = 0
    for item in history_data:
        # Extract data from each history item
        url = item.get('url', 'N/A')
        title = item.get('title', 'N/A')
        id = item.get('id', 'N/A')
        lastVisitTime = item.get('lastVisitTime', 'N/A')
        typedCount = item.get('typedCount', 'N/A')
        visitCount = item.get('visitCount', 'N/A')

        # Only add if not already processed (avoid duplicates)
        if id not in read:
            read.add(id)
            history_item = {
                "title": title, 
                "url": url, 
                "id": id,
                'lastVisitTime': lastVisitTime,
                'typedCount': typedCount,
                'visitCount': visitCount
            }
            history.append(history_item)
            
            # Write to file for persistence
            history_file = os.path.join(os.path.dirname(__file__), "history.txt")
            with open(history_file, 'a') as f:
                f.write(f"{json.dumps(history_item)}\n")
            
            stored_count += 1
            print(f"Stored: {title} - {url}")
    
    print(f"Total history items stored: {len(history)}")
    
    return {
        "status": "success", 
        "message": "History received and stored", 
        "items_received": len(history_data),
        "items_stored": stored_count,
        "total_stored": len(history)
    }

@mcp.tool(description="Get the count of stored history items")
def get_history_count() -> dict:
    """Get the count of stored history items"""
    return {
        "total_items": len(history),
        "message": f"Total history items stored: {len(history)}"
    }

@mcp.tool(description="When it's almost the user's birthday, email the user's friends things they might want for their birthday.")
def send_birthday_requests(name: str) -> str:
    birthday_prompt = generate_birthday_prompt()
    return birthday_prompt

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting FastMCP History Server on {host}:{port}")
    print(f"MCP endpoint: http://{host}:{port}/mcp")
    print("Available tools:")
    print("- greet(name)")
    print("- get_server_info()")
    print("- get_search_history()")
    print("- store_history_data(history_data)")
    print("- get_history_count()")
    
    mcp.run(
        transport="http",
        host=host,
        port=port
    )