import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from openai import OpenAI

app = Flask(__name__)

# 1. Connect to MongoDB using the Environment Variable you set on Render
mongo_client = MongoClient(os.environ.get("MONGO_URI"))
db = mongo_client.chatbot_db
history_col = db.chat_history

# 2. Setup OpenAI
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get("user_id")
    user_input = data.get("message")

    if not user_id or not user_input:
        return jsonify({"error": "Missing user_id or message"}), 400

    # 3. Fetch memory for this specific user
    user_doc = history_col.find_one({"user_id": user_id})
    # If no history exists, start a fresh conversation
    history = user_doc["history"] if user_doc else [{"role": "system", "content": "You are a helpful assistant."}]

    # 4. Add the user's new message to the history
    history.append({"role": "user", "content": user_input})

    # 5. Get AI response
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history
        )
        bot_reply = completion.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # 6. Save the new assistant message to history and update DB
    history.append({"role": "assistant", "content": bot_reply})
    history_col.update_one(
        {"user_id": user_id},
        {"$set": {"history": history}},
        upsert=True
    )

    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    # Render handles the port automatically
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))