from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
import os

from prompts import system_prompt
from tools import (
    toggle_light, set_ac_temperature, get_device_status, get_weather,
    get_latest_news, get_current_datetime, turn_on_ac, turn_off_ac,
    turn_on_tv, turn_off_tv, change_tv_channel, set_tv_volume,
    activate_guest_mode, stop_coffee_machine, start_coffee_machine,
    turn_off_all_lights, close_blinds, open_blinds, unlock_door, lock_door,
    turn_on_all_lights,
)

# Configure the LLM via LangChain
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"))  # best - limited
# llm = ChatGroq(model="llama3-70b-8192", temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"))          # powerful
# llm = ChatGroq(model="llama3-8b-8192", temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"))           # fast


tools = [
    toggle_light, set_ac_temperature, get_device_status, get_weather,
    get_latest_news, get_current_datetime, turn_on_ac, turn_off_ac,
    turn_on_tv, turn_off_tv, change_tv_channel, set_tv_volume,
    activate_guest_mode, stop_coffee_machine, start_coffee_machine,
    turn_off_all_lights, close_blinds, open_blinds, unlock_door, lock_door,
    turn_on_all_lights,
]

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=False
)