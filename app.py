import os
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# --- Database Setup ---
# Use the environment variable, but have a fallback for testing
mongo_uri = os.environ.get("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.chatbot_db
history_col = db.chat_history

print("MongoDB Client Initialized")

@app.route('/')
def home():
    return "Bot is online"

@app.route('/chat', methods=['POST'])
def chat():
    # Simple check to see if we can reach the DB
    try:
        # Just a dummy operation to see if the connection is alive
        count = history_col.count_documents({})
        return jsonify({"reply": f"Success! I can see {count} messages in the database."})
    except Exception as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run()