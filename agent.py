import os
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from tools import calculate_budget, search_flights, search_hotels


load_dotenv()


# 1. Doc System Prompt
SYSTEM_PROMPT = Path(__file__).with_name("system_prompt.txt").read_text(encoding="utf-8")


# 2. Khai bao State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# 3. Khoi tao LLM va Tools
tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatOpenAI(
    model="qwen/qwen3.6-plus:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)
llm_with_tools = llm.bind_tools(tools_list)


# 4. Agent Node
def agent_node(state: AgentState):
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)

    # === LOGGING ===
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"Goi tool: {tc['name']}({tc['args']})")
    else:
        print("Tra loi truc tiep")

    return {"messages": [response]}


# 5. Xay dung Graph
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)

tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")

graph = builder.compile()


# 6. Chat loop
if __name__ == "__main__":
    print("=" * 60)
    print("TravelBuddy - Tro ly Du lich Thong minh")
    print("Go 'quit' de thoat")
    print("=" * 60)

    while True:
        user_input = input("\nBan: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break

        print("\nTravelBuddy dang suy nghi...")
        result = graph.invoke({"messages": [("human", user_input)]})
        final = result["messages"][-1]
        print(f"\nTravelBuddy: {final.content}")
