import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
import openai

app = Flask(__name__)

# 1. Setup Database (Use an Environment Variable for your connection string on Render!)
# Go to Render Dashboard -> Your App -> Environment -> Add 'MONGO_URI'
client = MongoClient(os.environ.get("MONGO_URI"))
db = client.chatbot_db
history_col = db.chat_history

# 2. Configure AI (Use Environment Variable for API Key)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get("user_id")
    user_input = data.get("message")

    # A. Retrieve memory from MongoDB
    user_doc = history_col.find_one({"user_id": user_id})
    chat_history = user_doc["history"] if user_doc else []

    # B. Add current user message to history
    chat_history.append({"role": "user", "content": user_input})

    # C. Generate response from AI
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=chat_history
    )
    bot_reply = response.choices[0].message.content

    # D. Save updated history back to MongoDB
    chat_history.append({"role": "assistant", "content": bot_reply})
    history_col.update_one(
        {"user_id": user_id},
        {"$set": {"history": chat_history}},
        upsert=True
    )

    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    app.run()