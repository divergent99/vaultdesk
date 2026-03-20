import re

from langchain_core.messages import HumanMessage, AIMessage

from agent.graph import agent
from auth.ciba import set_current_user

# user_id -> list of LangChain messages
_conversations: dict[str, list] = {}


def run_agent(user_id: str, message: str) -> str:
    # Keep ciba.py in sync with who is making the request
    set_current_user(user_id)

    if user_id not in _conversations:
        _conversations[user_id] = []

    _conversations[user_id].append(HumanMessage(content=message))
    result = agent.invoke({"messages": _conversations[user_id]})
    _conversations[user_id] = result["messages"]

    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            content = re.sub(
                r"<thinking>.*?</thinking>", "", msg.content, flags=re.DOTALL
            ).strip()
            return content

    return "I couldn't process that request."


def clear_conversation(user_id: str) -> None:
    _conversations.pop(user_id, None)
