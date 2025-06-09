import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from rich.console import Console

# Import tools
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
    lock_door
)

# Load API key
load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    print("Error: GROQ_API_KEY not found.")
    exit()

# Console for display
console = Console()

# Initialize LLM
# llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)  # best model
llm = ChatGroq(model="llama3-70b-8192", temperature=0)
# llm = ChatGroq(model="llama3-8b-8192", temperature=0)   # faster

# Tools list
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
    lock_door
]

# Prompt template
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

# Agent creation
agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# Main loop
def main():
    console.print("[bold green]🤖 Smart Home Assistant Jarvis is active.[/bold green] Type 'exit' to quit.")

    chat_history = []

    while True:
        user_input = console.input("[bold blue]You: [/bold blue]")
        if user_input.lower() == 'exit':
            console.print("🤖 [bold red]Goodbye![/bold red]")
            break

        console.print("[yellow]Jarvis is thinking...[/yellow]")

        try:
            response = agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })

            console.print(f"[bold green]Assistant:[/bold green] {response['output']}")
            chat_history.extend([
                HumanMessage(content=user_input),
                AIMessage(content=response['output'])
            ])
            chat_history = chat_history[-10:]  # Keep last 10 messages

        except Exception as e:
            console.print(f"[bold red]An error occurred: {e}[/bold red]")


if __name__ == "__main__":
    main()


