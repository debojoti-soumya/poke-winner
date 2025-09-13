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

history = []
read = set()

@mcp.tool('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    print("status ok");
    return jsonify({"status": "healthy", "message": "Server is running"})

@mcp.tool('/receive_history', methods=['POST'])
def receive_history():
    print("=== RECEIVE_HISTORY ENDPOINT CALLED ===")
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")
    print(f"Request content type: {request.content_type}")
    
    """
    Endpoint to receive browser history data from the Chrome extension.
    """
    if not request.is_json:
        print("ERROR: Request is not JSON")
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    # Get the JSON data sent from the extension
    history_data = request.get_json()
    print(f"Received history data: {len(history_data) if history_data else 0} items")

    # Store the data
    if history_data:
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
                with open('history.txt', 'a') as f:
                    f.write(f"{json.dumps(history_item)}\n")
                
                print(f"Stored: {title} - {url}")
    else:
        print("Received an empty history list.")

    print(f"Total history items stored: {len(history)}")
    print("=== END RECEIVE_HISTORY ===")
    
    return jsonify({
        "status": "success", 
        "message": "History received and stored", 
        "items_received": len(history_data) if history_data else 0,
        "total_stored": len(history)
    })

@mcp.tool('/get_history', methods=['GET'])
def get_history():
    """Endpoint to retrieve all stored history data"""
    print("=== GET_HISTORY ENDPOINT CALLED ===")
    print(f"Returning {len(history)} history items")
    
    return jsonify({
        "status": "success",
        "message": "History data retrieved",
        "total_items": len(history),
        "data": history
    })

@mcp.tool('/get_history_file', methods=['GET'])
def get_history_file():
    """Endpoint to retrieve history data from file"""
    print("=== GET_HISTORY_FILE ENDPOINT CALLED ===")
    
    try:
        file_data = []
        if os.path.exists('history.txt'):
            with open('history.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        file_data.append(json.loads(line))
        
        print(f"Returning {len(file_data)} items from file")
        return jsonify({
            "status": "success",
            "message": "History data retrieved from file",
            "total_items": len(file_data),
            "data": file_data
        })
    except Exception as e:
        print(f"Error reading file: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error reading history file: {str(e)}"
        }), 500

if __name__ == "__main__":
    # Use the main port for Flask (Render requirement)
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"
    
    print(f"MCP endpoint: http://{host}:{port}/mcp")
    
    mcp.run(
        transport="http",
        host=host,
        port=port
    )
