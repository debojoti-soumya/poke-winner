#!/usr/bin/env python3
"""
Simple Flask server to receive history data from Chrome extension
and store it using the MCP server
"""
from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# MCP server URL (will be the same server but different port)
MCP_SERVER_URL = "http://localhost:8000/mcp"

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "History receiver is running"})

@app.route('/receive_history', methods=['POST'])
def receive_history():
    """Receive history data from Chrome extension and store via MCP"""
    print("=== RECEIVE_HISTORY ENDPOINT CALLED ===")
    
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    # Get the JSON data sent from the extension
    history_data = request.get_json()
    print(f"Received history data: {len(history_data) if history_data else 0} items")

    # Store the data using MCP
    try:
        # Call the MCP store_history_data tool
        response = requests.post(
            f"{MCP_SERVER_URL}/tools/store_history_data",
            json={"arguments": {"history_data": history_data}},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Successfully stored data via MCP: {result}")
            return jsonify({
                "status": "success",
                "message": "History received and stored via MCP",
                "mcp_result": result
            })
        else:
            print(f"MCP call failed: {response.status_code} - {response.text}")
            return jsonify({
                "status": "error",
                "message": "Failed to store data via MCP"
            }), 500
            
    except Exception as e:
        print(f"Error calling MCP: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error calling MCP: {str(e)}"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", 5000))
    host = "0.0.0.0"
    
    print(f"Starting Flask History Receiver on {host}:{port}")
    print(f"Health check: http://{host}:{port}/")
    print(f"Receive history: http://{host}:{port}/receive_history")
    
    app.run(host=host, port=port, debug=False)
