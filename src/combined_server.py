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
@mcp.tool(description="Get all stored browser history. Requires Poke user email as a string in the format useremail@example.com")
def get_browser_history(user_email : str) -> list:
    """Get browser history from remote URL"""
    try:
        import requests
        
        # Fetch browser history from remote URL
        url = "http://10.29.175.237:5001/receive_history"
        # url = url + "?user" + user_email
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



# -------------------
# Additional MCP tool: Bookmarks
# -------------------
@mcp.tool(description="Get all stored browser bookmarks. Requires Poke user email as a string in the format useremail@example.com")
def get_bookmarks(user_email : str) -> list:
    """Get bookmarks from remote URL"""
    try:
        import requests

        # Base URL can be overridden via env var to avoid hard-coding
        base_url = os.environ.get("BOOKMARKS_API_URL", "http://10.29.175.237:5001/bookmarks")
        url = base_url # f"{base_url}?user={user_email}"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            bookmarks_data = response.json()
            # Expecting a list response; guard against non-list JSON
            if isinstance(bookmarks_data, list):
                print(f"Retrieved {len(bookmarks_data)} bookmarks from {url}")
                return bookmarks_data
            else:
                print("Bookmarks response JSON is not a list; returning empty list")
                return []
        else:
            print(f"Error fetching bookmarks: HTTP {response.status_code}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error fetching bookmarks from URL: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing bookmarks JSON response: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in get_bookmarks: {e}")
        return []


if __name__ == "__main__":
    # Start Flask on one port, MCP on another

    print(f"Starting MCP on http://localhost:{MCP_PORT}")
    print("MCP tool available: get_browser_history()")
    print("MCP tool available: get_bookmarks()")
    mcp.run(transport="http", host="0.0.0.0", stateless_http=True, port=MCP_PORT)
