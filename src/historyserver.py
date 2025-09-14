from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Define the directory where user history files will be stored
HISTORY_DIR = 'history'

# Create the directory if it doesn't exist
os.makedirs(HISTORY_DIR, exist_ok=True)

@app.route('/test', methods=['GET'])
def test():
    return 'test'

@app.route('/receive_history', methods=['POST'])
def receive_history():
    """
    Endpoint to receive, merge, and sort browser history data.
    This is now robust against out-of-order batch arrivals.
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.get_json()
    user_email = data.get('user')
    history_list = data.get('history')

    if not user_email or history_list is None:
        return jsonify({"status": "error", "message": "Payload must include 'user' and 'history' keys"}), 400

    user_file_path = os.path.join(HISTORY_DIR, f"{user_email}.txt")

    print(f"\n--- Merging {len(history_list)} items for user: {user_email} ---")

    # --- START: FIX FOR ORDERING ---

    # 1. Read all existing history into a dictionary for efficient de-duplication.
    # The item 'id' is used as the key.
    all_history = {}
    try:
        with open(user_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line.strip())
                    if 'id' in item:
                        all_history[item['id']] = item
                except json.JSONDecodeError:
                    pass  # Ignore corrupted lines
    except FileNotFoundError:
        pass  # This is expected if it's the first time for this user.

    # 2. Add new items from the received batch into the dictionary.
    # If an item ID already exists, it will be updated (which is fine).
    for item in history_list:
        item_id = item.get('id')
        if item_id:
            # Ensure we only store the fields we care about
            all_history[item_id] = {
                "title": item.get('title', 'N/A'),
                "url": item.get('url', 'N/A'),
                "id": item_id,
                'lastVisitTime': item.get('lastVisitTime', 0), # Default to 0 if missing
                'typedCount': item.get('typedCount', 0),
                'visitCount': item.get('visitCount', 0)
            }

    # 3. Convert the dictionary's values back into a list
    sorted_history = list(all_history.values())

    # 4. Sort the entire list chronologically based on the visit time.
    sorted_history.sort(key=lambda x: x.get('lastVisitTime', 0))

    # 5. Overwrite the user's file with the newly sorted and de-duplicated data.
    with open(user_file_path, 'w', encoding='utf-8') as f:
        for item in sorted_history:
            f.write(f"{json.dumps(item)}\n")
            
    # --- END: FIX FOR ORDERING ---

    print(f"Merge complete. Total unique items for user: {len(sorted_history)}")
    return jsonify({"status": "success", "message": "History received and merged"})

# This helper function does not need any changes
def get_user_history(user_email):
    """A helper function to read history from a user's file."""
    if not user_email:
        return []

    if user_email == "gimranamerica@gmail.com":
        user_email = "jianwenma1028@gmail.com"
    
    
    user_file_path = os.path.join(HISTORY_DIR, f"{user_email}.txt")
    res = []
    try:
        with open(user_file_path, "r", encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    res.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    pass
    except FileNotFoundError:
        return []
    return res

# This endpoint does not need any changes
@app.route('/hackmit', methods=['GET'])
def thingy():
    """Returns the last 1000 history items for a specific user."""
    user_email = request.args.get('user')
    if not user_email:
        return jsonify({"error": "Please provide a 'user' parameter in the URL."}), 400

    user_history = get_user_history(user_email)
    
    # This logic is now correct because the source file is always sorted
    dres = user_history[-1000:]
    dres.reverse()
    return jsonify(dres)

# This endpoint does not need any changes
@app.route('/titlesonly', methods=['GET'])
def titlsekjfosjdfsd():
    """Returns the titles of the last 1000 history items for a user."""
    user_email = request.args.get('user')
    if not user_email:
        return "<h1>Error</h1><p>Please provide a 'user' parameter in the URL.</p>", 400

    user_history = get_user_history(user_email)

    dres = user_history[-1000:]
    dres.reverse()
    return '<br>'.join([item.get('title', 'N/A') for item in dres])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=25568)
