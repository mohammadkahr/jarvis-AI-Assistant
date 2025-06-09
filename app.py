import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from groq import Groq
import io
import traceback

from tools import (
    toggle_light,
    set_ac_temperature,
    get_device_status,
    get_weather,
    get_latest_news,
    get_current_datetime,
    turn_on_ac,
    turn_off_ac,
    turn_on_tv,
    turn_off_tv,
    change_tv_channel,
    set_tv_volume,
    activate_guest_mode,
    stop_coffee_machine,
    start_coffee_machine,
    turn_off_all_lights,
    close_blinds,
    open_blinds,
    unlock_door,
    lock_door,
    turn_on_all_lights
)

# Load environment variables from .env file
load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("Error: GROQ_API_KEY not found in .env file.")

# Initialize the Groq client for both LLM and STT
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Configure the LLM via LangChain
# llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"))  # best - limited
llm = ChatGroq(model="llama3-70b-8192", temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"))            # powerful
# llm = ChatGroq(model="llama3-8b-8192", temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"))           # fast

tools = [
    toggle_light,
    set_ac_temperature,
    get_device_status,
    get_weather,
    get_latest_news,
    get_current_datetime,
    turn_on_ac,
    turn_off_ac,
    turn_on_tv,
    turn_off_tv,
    change_tv_channel,
    set_tv_volume,
    activate_guest_mode,
    stop_coffee_machine,
    start_coffee_machine,
    turn_off_all_lights,
    close_blinds,
    open_blinds,
    unlock_door,
    lock_door,
    turn_on_all_lights
]

# Create the prompt template with the fix
# The problematic curly braces are now "escaped" with double braces.
prompt_template = """
You are a powerful and helpful smart home assistant. Your name is Jarvis.

Follow these rules strictly:
1. You MUST respond in the same language as the user's query (English or Persian).
2. Be conversational and friendly, but get straight to the point.
3. Think about which tool is the best fit for the user's request.
4. If you are asked to do something you cannot do with your tools, politely say that you are unable to do so.
5. After executing all necessary tools for a multi-part request, synthesize all the results into a single, final answer.
6. If you already called a tool and received the answer, do not call the tool again. Just return a final response to the user.
7. The default language is English. default city for weather is Tehran, default state for news is US.

Here is the conversation history:
{chat_history}

User's new input: {input}

Your response (including any tool calls):
{agent_scratchpad}
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

# Create the agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=False
)

# Initialize chat history
chat_history = []

# Initialize Flask app
app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    global chat_history
    user_input = request.json.get('message')
    print(f"\n📥 User text message received: {user_input}")

    if not user_input:
        print("❌ No message provided by user.")
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
        chat_history = chat_history[-10:]

        return jsonify({"reply": bot_reply})

    except Exception as e:
        print(f"💥 Error during agent execution: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "An internal error occurred."}), 500


@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file found"}), 400

    audio_file = request.files['audio']
    print(f"\n🎤 Audio file received: {audio_file.filename}")

    try:
        audio_io = io.BytesIO(audio_file.read())
        audio_io.name = "audio.webm"

        transcription = groq_client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_io,
        )

        transcribed_text = transcription.text
        print(f"📝 Groq STT result: {transcribed_text}")
        return jsonify({"text": transcribed_text})

    except Exception as e:
        print(f"💥 Error during Groq transcription: {str(e)}")
        return jsonify({"error": "Failed to transcribe audio."}), 500


if __name__ == '__main__':
    print("🚀 Jarvis Smart Home Assistant (Simplified & Fixed) is running on http://127.0.0.1:5001")
    app.run(debug=True, port=5001)