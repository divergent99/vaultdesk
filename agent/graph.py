from datetime import datetime
from typing import Annotated, TypedDict

from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from agent.prompts import SYSTEM_PROMPT
from services.llm_client import llm
from tools.registry import TOOLS


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


llm_with_tools = llm.bind_tools(TOOLS)


def agent_node(state: AgentState):
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    date_context = (
        f"\n\nCurrent date: {today}. Current time: {current_time}. "
        "Use this exact date for today/tomorrow/this week."
    )
    msgs = [SystemMessage(content=SYSTEM_PROMPT + date_context)] + state["messages"]
    return {"messages": [llm_with_tools.invoke(msgs)]}


def should_continue(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")
    return graph.compile()


# Module-level compiled agent — imported by runner
agent = build_graph()
