import os
import traceback
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from groq import Groq
import io
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Error: GROQ_API_KEY not found in .env file.")

app = Flask(__name__)
CORS(app)
groq_client = Groq(api_key=GROQ_API_KEY)

device_states = {
    "lights": {
        "kitchen": "off",
        "bathroom": "off",
        "room1": "off",
        "room2": "off",
    },
    "ac": {
        "room1": {"state": "off", "temp": 22},
        "kitchen": {"state": "off", "temp": 22},
    },
    "tv": {
        "living_room": "off"
    }
}


@tool
def control_light(location: str, state: str) -> str:
    """
    Turns a light on or off in a specific location.
    Valid locations are: 'kitchen', 'bathroom', 'room1', 'room2'.
    Valid states are: 'on', 'off'.
    """
    global device_states
    location = location.lower().replace(" ", "")
    state = state.lower()
    if location in device_states["lights"] and state in ["on", "off"]:
        device_states["lights"][location] = state
        print(f"✅ ACTION: Light in {location} turned {state}.")
        return f"Success! The light in the {location} has been turned {state}."
    return f"Error: Invalid location or state for the light. Location: {location}, State: {state}"


@tool
def control_ac(location: str, state: str, temperature: int = None) -> str:
    """
    Controls the AC unit. Can turn it on/off and set the temperature.
    Valid locations are: 'room1', 'kitchen'.
    Valid states are: 'on', 'off'.
    Temperature is an integer.
    """
    global device_states
    location = location.lower().replace(" ", "")
    state = state.lower()
    if location in device_states["ac"]:
        if state in ["on", "off"]:
            device_states["ac"][location]["state"] = state
            response_msg = f"AC in {location} turned {state}."
        if temperature:
            device_states["ac"][location]["temp"] = temperature
            response_msg += f" and temperature set to {temperature}°C."
        print(f"✅ ACTION: {response_msg}")
        return f"Success! {response_msg}"
    return f"Error: Invalid location for the AC. Location: {location}"


tools = [control_light, control_ac]

llm = ChatGroq(model="llama3-70b-8192", groq_api_key=GROQ_API_KEY)
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful smart home assistant named Jarvis. You control lights and AC units. Respond concisely and confirm the action."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
chat_history = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    global chat_history
    user_input = request.json.get('message')
    print(f"\n📥 User text message received: {user_input}")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history
        })
        bot_reply = response.get('output', "I'm sorry, I couldn't process that.")
        print(f"🤖 Jarvis reply: {bot_reply}")

        chat_history.extend([HumanMessage(content=user_input), AIMessage(content=bot_reply)])
        chat_history = chat_history[-10:]

        return jsonify({"reply": bot_reply})
    except Exception as e:
        print(f"💥 Error during agent execution: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal error occurred."}), 500


@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file found"}), 400
    audio_file = request.files['audio']
    try:
        audio_io = io.BytesIO(audio_file.read())
        audio_io.name = audio_file.filename
        transcription = groq_client.audio.transcriptions.create(model="whisper-large-v3", file=audio_io)
        return jsonify({"text": transcription.text})
    except Exception as e:
        print(f"💥 Error during Groq transcription: {e}")
        return jsonify({"error": "Failed to transcribe audio."}), 500


@app.route('/get_device_states', methods=['GET'])
def get_device_states():
    """
    This endpoint sends the status of all devices to the ESP32 in JSON format.
    """
    print(f"\n📡 ESP32 is requesting device states. Sending: {device_states}")
    return jsonify(device_states)


if __name__ == '__main__':
    print("🚀 Jarvis Smart Home Assistant is running.")
    print("📢 Waiting for commands from the web UI and state requests from ESP32...")
    app.run(host='0.0.0.0', port=5001, debug=True)
