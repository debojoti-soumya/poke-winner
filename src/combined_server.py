#!/usr/bin/env python3
import os, json, threading
from flask import Flask, request, jsonify
from fastmcp import FastMCP
from datetime import datetime
from txtai import Embeddings

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
    """Get browser history"""
    print("getting history-------")
    try:
        import requests
        
        # Fetch browser history from remote URL
        url = "http://24.16.153.94:25568/hackmit?user=jianwenma1028@gmail.com"
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

# @mcp.tool(description="Find out what the user is doing right now and make sure they are on task.")
# def checkin():
#     history = get_browser_history()
#     current_time = datetime.now().time()
#     current_activity = None
#     if current_time - history[0]["lastVisitTime"] < 900000:
#         current_activity = history[0]["url"]
#     if current_activity:
#         return f"User is/was recently browsing this website: {current_activity}. If it is productive, text them Good job! If it is not productive, text them to get back on task."
#     else:
#         return "User is probably not browsing the Internet right now. Ignore."


@mcp.tool(description="Find semantically similar items")
def find_semantically_similar(s: str) -> list:
    """Find semantically similar items in browser history"""
    history = get_browser_history()
    if not history:
        return []
    texts = [item.get("title", "") + " " + item.get("url", "") for item in history]

    embeddings = Embeddings({"method": "transformers", "path": "sentence-transformers/all-MiniLM-L6-v2"})
    embeddings.index((uid, text, None) for uid, text in enumerate(texts))
    results = embeddings.search(s, 5)
    similar_items = [history[uid] for uid, _ in results]
    return similar_items

@mcp.tool(description="Get search history for a segment of time (natural language, e.g. '9am', 'now', '10 minutes ago')")
def get_search_history(start_time: str, end_time: str) -> list:
    """Get search history between start_time and end_time (natural language time)"""
    import dateparser
    from datetime import datetime

    # Parse natural language time to datetime
    def nl_to_ms(tstr):
        dt = dateparser.parse(tstr)
        if not dt:
            raise ValueError(f"Could not parse time: {tstr}")
        t = dt.time()
        return (t.hour * 3600 + t.minute * 60 + t.second) * 1000

    try:
        start_ms = nl_to_ms(start_time)
        end_ms = nl_to_ms(end_time)
    except Exception as e:
        print(f"Error parsing time: {e}")
        return []

    history = get_browser_history()
    if not history:
        return []
    searches = [
        item for item in history
        if "search" in item.get("url", "").lower()
        and start_ms <= item["lastVisitTime"] <= end_ms
    ]
    return searches

@mcp.tool(description="Get the last n search history items")
def last_n_searches(n: int) -> list:
    """Get the last n search history items"""
    history = get_browser_history()
    if not history:
        return []
    return history[:n]

@mcp.tool(description="Flex out poke's ability. Use this function when users asks what poke is capable of, or when the conversation has just started. Returns the list of some example functions Poke can do. Poke then show off what its capable of to the user, in its own words.")
def flex():
    """Flex out poke's ability. Use this function when users asks what poke is capable of, or when the conversation has just started."""
    return "- ask me to check that you are staying focused (not visiting distracting webstes) every 5 minutes (or any other time interval!)" \
    "- chat with what you've seen today" \
    "- suggest you something interesting to read from the bookmarks you've saved" \
    "- roast me using my web history, or even ask to roast me on what I've been browsing in the last 5 minutes" \
    "- reflect on how did your day go" \
    "- ask me to check help set your daily goals and check in with you on your progress every hour" \
    "- anything else you can think of!"
    # return "Poke is a powerful AI assistant that can help you with a variety of tasks, including browsing the web, managing your schedule, and more. Just ask!"

if __name__ == "__main__":
    # Start Flask on one port, MCP on another

    print(f"Starting MCP on http://localhost:{MCP_PORT}")
    print("MCP tool available: get_browser_history()")
    mcp.run(transport="http", host="0.0.0.0", stateless_http=True, port=MCP_PORT)
