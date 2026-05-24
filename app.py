import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is online"

@app.route('/chat', methods=['POST'])
def chat():
    return jsonify({"reply": "Success"})

if __name__ == '__main__':
    app.run()