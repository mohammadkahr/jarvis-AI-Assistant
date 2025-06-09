import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage

# Import all tools from our tools file
from tools import (
    toggle_light,
    set_ac_temperature,
    get_device_status,
    get_weather,
    get_latest_news,
    get_current_datetime,
    change_tv_channel,
    turn_on_tv,
    lock_door,
    unlock_door,
    open_blinds,
    close_blinds,
    activate_sleep_mode,
    activate_guest_mode
)

load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    print("Error: GOOGLE_API_KEY not found. Make sure it is set in your .env file.")
    exit()


llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0)


tools = [
    toggle_light,            # Turns a specific room's light on or off
    set_ac_temperature,      # Sets the AC temperature and turns it on if needed
    get_device_status,       # Retrieves the current status of all or selected devices
    get_weather,             # Gets the current weather for Tehran
    get_latest_news,         # Fetches the top news headlines for a specified country
    get_current_datetime,    # Returns the current date and time
    change_tv_channel,       # Changes the TV channel in the living room
    turn_on_tv,              # Turns on the TV in the living room
    lock_door,               # Locks the door in the specified location
    unlock_door,             # Unlocks the door in the specified location
    open_blinds,             # Opens the blinds in the specified location
    close_blinds,            # Closes the blinds in the specified location
    activate_sleep_mode,     # Activates sleep mode: dims lights, lowers AC, etc.
    activate_guest_mode      # Activates guest mode: adjusts lights, temperature, and opens blinds
]

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

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def main():
    print("🤖 Smart Home Assistant (using Gemini) is active. Type 'exit' to quit.")
    chat_history = []
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("🤖 Goodbye!")
            break

        try:
            result = agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })
            print(f"Assistant: {result['output']}")

            chat_history.extend([
                HumanMessage(content=user_input),
                AIMessage(content=result["output"])
            ])
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()