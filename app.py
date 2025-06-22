import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from groq import Groq
import io
import traceback
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Error: GROQ_API_KEY not found in .env file.")

from agent_setup import agent_executor

app = Flask(__name__)
CORS(app)
groq_client = Groq(api_key=GROQ_API_KEY)
chat_history = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    global chat_history
    user_input = request.json.get('message')
    print(f"\nUser text message received: {user_input}")

    if not user_input:
        print("No message provided by user.")
        return jsonify({"error": "No message provided"}), 400

    try:
        response = agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history
        })

        bot_reply = response.get('output', "I'm sorry, I couldn't process that.")
        print(f"🤖 Jarvis reply: {bot_reply}")

        chat_history.extend([
            HumanMessage(content=user_input),
            AIMessage(content=bot_reply)
        ])
        chat_history = chat_history[-100:]

        return jsonify({"reply": bot_reply})

    except Exception as e:
        error_message = f"Error during agent execution: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({"error": "An internal error occurred."}), 500


@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file found"}), 400

    audio_file = request.files['audio']
    print(f"\nAudio file received: {audio_file.filename}")

    try:
        audio_io = io.BytesIO(audio_file.read())
        audio_io.name = audio_file.filename

        transcription = groq_client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_io,
        )

        transcribed_text = transcription.text
        print(f"Groq STT result: {transcribed_text}")
        return jsonify({"text": transcribed_text})

    except Exception as e:
        error_message = f"Error during Groq transcription: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({"error": "Failed to transcribe audio."}), 500


if __name__ == '__main__':
    print("🚀 Jarvis Smart Home Assistant is running on http://127.0.0.1:5001")
    app.run(debug=True, port=5001)
