#!/usr/bin/env python3
import os, json, threading
from flask import Flask, request, jsonify
from fastmcp import FastMCP

# -------------------
# Setup
# -------------------
HISTORY_FILE = "/tmp/browser_history.txt"
FLASK_PORT = 2000
MCP_PORT = 8000

# MCP server
mcp = FastMCP("Browser History MCP Server")

# Flask app
app = Flask(__name__)

# -------------------
# MCP tool
# -------------------
@mcp.tool(description="Get all stored browser history")
def get_browser_history() -> list:
    """Get browser history from remote URL"""
    try:
        import requests
        
        # Fetch browser history from remote URL
        url = "http://24.16.153.94:25568/hackmit"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            history_data = response.json()
            print(f"Retrieved {len(history_data)} browser history items from {url}")
            return history_data
        else:
            print(f"Error fetching browser history: HTTP {response.status_code}")
            return []
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching browser history from URL: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []



if __name__ == "__main__":
    # Start Flask on one port, MCP on another

    print(f"Starting MCP on http://localhost:{MCP_PORT}")
    print("MCP tool available: get_browser_history()")
    mcp.run(transport="http", host="0.0.0.0", port=MCP_PORT)
