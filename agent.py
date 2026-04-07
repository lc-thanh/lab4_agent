import os
import logging
import sys
import time
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from logging_utils import configure_logging, log_lines
from tools import calculate_budget, search_flights, search_hotels


load_dotenv()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


configure_logging()
logger = logging.getLogger(__name__)


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
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools_list)


def invoke_with_retry(messages: list, max_attempts: int = 3):
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return llm_with_tools.invoke(messages)
        except Exception as exc:
            last_error = exc
            logger.warning("LLM call failed (attempt %s/%s): %s", attempt, max_attempts, exc)
            if attempt < max_attempts:
                time.sleep(attempt)
    raise last_error


# 4. Agent Node
def agent_node(state: AgentState) -> AgentState:
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = invoke_with_retry(messages)

    if response.tool_calls:
        for tc in response.tool_calls:
            logger.info("Gọi tool: %s(%s)", tc["name"], tc["args"])
    else:
        logger.info("Trả lời trực tiếp")

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
    log_lines(logger, logging.INFO, "=" * 60)
    log_lines(logger, logging.INFO, "TravelBuddy - Trợ lý Du lịch Thông minh")
    log_lines(logger, logging.INFO, "Gõ 'quit' để thoát.")
    log_lines(logger, logging.INFO, "=" * 60)

    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break

        log_lines(logger, logging.INFO, "TravelBuddy đang suy nghĩ...")
        result = graph.invoke({"messages": [("human", user_input)]})
        final = result["messages"][-1]
        log_lines(logger, logging.INFO, f"TravelBuddy: {final.content}")
