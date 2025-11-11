from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class EmailState(TypedDict):
    email: str
    category: Literal["spam", "normal", "urgent"]
    priority_score: int
    response: str


def categorize_email(state: EmailState):
    email = state["email"].lower()

    if "urgent" in email or "asap" in email:
        category = "urgent"
    elif "offer" in email or "discount" in email:
        category = "spam"
    else:
        category = "normal"

    return {"category": category}


def assign_priority(state: EmailState):
    scores = {"urgent": 10, "normal": 5, "spam": 1}
    return {"priority_score": scores[state["category"]]}


def draft_response(state: EmailState):
    responses = {
        "urgent": "가능한 빨리 답변드리겠습니다.",
        "normal": "귀하의 이메일을 확인했습니다. 곧 답변드리겠습니다.",
        "spam": "이 이메일은 스팸으로 분류되었습니다.",
    }
    return {"response": responses[state["category"]]}


graph_builder = StateGraph(EmailState)

graph_builder.add_node("categorize_email", categorize_email)
graph_builder.add_node("assign_priority", assign_priority)
graph_builder.add_node("draft_response", draft_response)

graph_builder.add_edge(START, "categorize_email")
graph_builder.add_edge("categorize_email", "assign_priority")
graph_builder.add_edge("assign_priority", "draft_response")
graph_builder.add_edge("draft_response", END)

graph = graph_builder.compile()

result = graph.invoke(
    {
        "email": "This is an urgent request for a discount offer.",
    }
)

print(result)
