import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage

from tools import (
    toggle_light, set_ac_temperature, get_device_status, get_weather,
    get_latest_news, get_current_datetime, change_tv_channel, turn_on_tv,
    lock_door, unlock_door, open_blinds, close_blinds,
    activate_sleep_mode, activate_guest_mode
)

# بارگذاری کلید API
load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("❌ Error: GROQ_API_KEY not found in .env file.")

# تعریف مدل LLM
llm = ChatGroq(model="llama3-70b-8192", temperature=0)

# تعریف ابزارها
tools = [
    toggle_light, set_ac_temperature, get_device_status, get_weather,
    get_latest_news, get_current_datetime, change_tv_channel, turn_on_tv,
    lock_door, unlock_door, open_blinds, close_blinds,
    activate_sleep_mode, activate_guest_mode
]

# ساخت prompt و agent
prompt_template = """
You are a powerful and helpful smart home assistant. Your name is Jarvis.

Follow these rules strictly:
1. You MUST respond in the same language as the user's query (Persian or English).
2. Be conversational and friendly, but get straight to the point.
3. Think about which tool is the best fit for the user's request.
4. If you are asked to do something you cannot do with your tools, politely say that you are unable to do so.
5. After executing all necessary tools for a multi-part request, synthesize all the results into a single, final answer.
6. If you already called a tool and received the answer, do not call the tool again. Just return a final response to the user.

Here is the conversation history:
{chat_history}

User's new input: {input}

Your response (including any tool calls):
{agent_scratchpad}
"""
prompt = ChatPromptTemplate.from_template(prompt_template)
agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

chat_history = []

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    global chat_history

    user_input = request.json.get('message')
    print(f"\n📥 User message received: {user_input}")

    if not user_input:
        print("❌ No message provided by user.")
        return jsonify({"error": "No message provided"}), 400

    try:
        response = agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history
        })

        print(f"🤖 Jarvis reply: {response['output']}")

        chat_history.extend([
            HumanMessage(content=user_input),
            AIMessage(content=response['output'])
        ])
        chat_history = chat_history[-10:]

        return jsonify({"reply": response['output']})

    except Exception as e:
        print(f"💥 Error occurred during processing: {str(e)}")
        return jsonify({"error": "An internal error occurred."}), 500


if __name__ == '__main__':
    print("🚀 Flask app running at http://localhost:5001")
    app.run(debug=True, port=5001)
