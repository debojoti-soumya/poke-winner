#!/usr/bin/env python3
import os
import json
from fastmcp import FastMCP
from flask import Flask, request, jsonify
import threading

# Initialize FastMCP server
mcp = FastMCP("Browser History MCP Server")

# Initialize Flask app
app = Flask(__name__)

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

# Flask endpoints
@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Combined server is running"})

@app.route('/receive_history', methods=['POST'])
def receive_history():
    """Receive browser history from Chrome extension and store in file"""
    print("=== RECEIVING BROWSER HISTORY ===")
    
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    # Get the browser history data from the extension
    history_data = request.get_json()
    print(f"Received {len(history_data) if history_data else 0} browser history items")

    # Store the data directly in file
    try:
        if not history_data:
            return jsonify({"status": "error", "message": "No history data provided"})
        
        # Use absolute path to ensure both servers use the same file
        history_file = "/tmp/browser_history.txt"
        stored_count = 0
        
        for item in history_data:
            # Write each history item to file
            with open(history_file, 'a') as f:
                f.write(f"{json.dumps(item)}\n")
            stored_count += 1
            print(f"Stored: {item.get('title', 'Unknown')} - {item.get('url', 'Unknown')}")
        
        print(f"Successfully stored {stored_count} browser history items in file")
        
        return jsonify({
            "status": "success", 
            "message": "Browser history stored successfully in file", 
            "items_stored": stored_count
        })
        
    except Exception as e:
        print(f"Error storing browser history: {e}")
        return jsonify({
            "status": "error", 
            "message": f"Error storing history: {str(e)}"
        }), 500

def run_flask():
    """Run Flask server in a separate thread"""
    flask_port = int(os.environ.get("FLASK_PORT", 5000))
    print(f"Starting Flask server on 0.0.0.0:{flask_port}")
    app.run(host='0.0.0.0', port=flask_port, debug=False)

if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start FastMCP server in main thread
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting Combined Server on {host}:{port}")
    print(f"Flask endpoint: http://0.0.0.0:5000/receive_history")
    print(f"MCP endpoint: http://{host}:{port}/mcp")
    print("Available MCP tools:")
    print("- get_browser_history() - Get all stored browser history")
    
    mcp.run(
        transport="http",
        host=host,
        port=port
    )
