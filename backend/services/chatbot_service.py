from flask import Blueprint, request, jsonify
import requests
import time


def send_chatbot_response():
    client = request.get_json()
    user_input = client.get("message")

    reply = ask_qwen(user_input)

    return jsonify({
        "reply" : reply
    })


def ask_qwen(user_input):

    start = time.time()

    response = requests.post("http://localhost:11434/api/generate",
        json={
            "model": "phi3:mini",
            "prompt": f"""
            Ask directly and briefly and provide concise responses. 
            Do not show chain-of-thought or reasoning process.
            Keep words under 150 unless asked otherwise by the user.

            JUST give the answer to the question in one or two sentences. 
            no extra fluff.

            USER: {user_input}
            """,
            "stream": False
        }
    )

    print("Qwen time:", time.time() - start)

    data = response.json()

    # Return chatbot response.
    return data["response"]