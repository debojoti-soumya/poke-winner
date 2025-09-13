#!/usr/bin/env python3
import os
from fastmcp import FastMCP
import requests
import json

mcp = FastMCP("Sample MCP Server")

@mcp.tool(description="Greet a user by name with a welcome message from the MCP server")
def greet(name: str) -> str:
    return f"Hello, {name}! Welcome to our sample MCP server running on Heroku!"

@mcp.tool(description="Get information about the MCP server including name, version, environment, and Python version")
def get_server_info() -> dict:
    return {
        "server_name": "Sample MCP Server",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": os.sys.version.split()[0]
    }

@mcp.tool(description="get search history")
def get_search_history() -> list:
    import json
    import os
    # Use the same file path as the Flask server
    history_file = os.path.join(os.path.dirname(__file__), "history.txt")
    res = []
    
    # Check if file exists, return empty list if it doesn't
    if not os.path.exists(history_file):
        return res
    
    try:
        with open(history_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    res.append(json.loads(line))
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading history file: {e}")
        return []
    
    return res


from flask import Flask, request, jsonify
import logging
import json
import os

# Suppress the default Flask startup messages
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

history = []
read = set()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Server is running"})

@app.route('/receive_history', methods=['POST'])
def receive_history():

    print("I'm here")
    """
    Endpoint to receive browser history data from the Chrome extension.
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    # Get the JSON data sent from the extension
    history_data = request.get_json()


    #print("\n--- Received Browser History ---")

    with open('history.txt', 'a') as f:
        if history_data:
            for item in history_data:
                # You can now process each history item as needed for your MCP automation.
                # For this example, we'll just print the URL and title.
                url = item.get('url', 'N/A')
                title = item.get('title', 'N/A')
                id = item.get('id', 'N/A')
                lastVisitTime = item.get('lastVisitTime', 'N/A')
                typedCount = item.get('typedCount', 'N/A')
                visitCount = item.get('visitCount', 'N/A')

                if id not in read:
                    read.add(id)
                    history.append({"title": title, "url": url, "id": id,
                                    'lastVisitTime': lastVisitTime,
                                    'typedCount': typedCount,
                                    'visitCount': visitCount
                                    })
                    f.write(f"{json.dumps(history[-1])}\n")

        else:
            print("Received an empty history list.")
        print(len(history))

    

    # Send a confirmation response back to the extension
    return jsonify({"status": "success", "message": "History received"})



if __name__ == "__main__":
    # Use the main port for Flask (Render requirement)
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"
    
    print(f"Starting Flask server with MCP endpoints on {host}:{port}")
    print(f"Flask endpoint: http://{host}:{port}/receive_history")
    print(f"MCP endpoint: http://{host}:{port}/mcp")
    
    app.run(host=host, port=port, debug=False)
