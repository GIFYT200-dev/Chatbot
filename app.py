import os
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# --- Database Setup ---
# Ensure MONGO_URI is set in your Render Environment Variables
mongo_uri = os.environ.get("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.chatbot_db
history_col = db.chat_history

print("MongoDB Client Initialized")

@app.route('/')
def home():
    # This route now shows you the current message count
    count = history_col.count_documents({})
    return f"Bot is online! Total messages in database: {count}"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # 1. Save to MongoDB
    chat_entry = {
        "user_message": user_message,
        "bot_reply": "This is a placeholder reply."
    }
    history_col.insert_one(chat_entry)

    # 2. Return confirmation
    return jsonify({
        "reply": "Message saved successfully!",
        "saved_message": user_message
    })

if __name__ == '__main__':
    app.run()