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

@app.route('/receive_history', methods=['POST'])
def receive_history():
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

if __name__ == '__main__':
    # Get port from environment variable (for Render deployment) or use default
    port = int(os.environ.get('PORT', 1000))
    host = '0.0.0.0'  # Use 0.0.0.0 for deployment, 127.0.0.1 for local only
    
    print("Starting MCP server...")
    print(f"Listening for browser history on http://{host}:{port}/receive_history")
    
    app.run(host=host, port=port)



