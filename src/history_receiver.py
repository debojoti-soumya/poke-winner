#!/usr/bin/env python3
"""
Simple Flask server to receive browser history from Chrome extension
and store it using the MCP server
"""
from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# MCP server URL - this will be your deployed MCP server
MCP_SERVER_URL = "https://poke-winner.onrender.com/mcp"

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "History receiver is running"})

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

if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", 5000))
    host = "0.0.0.0"
    
    print(f"Starting Flask History Receiver on {host}:{port}")
    print(f"Health check: http://{host}:{port}/")
    print(f"Receive history: http://{host}:{port}/receive_history")
    
    app.run(host=host, port=port, debug=False)