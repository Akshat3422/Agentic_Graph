from langgraph.graph import StateGraph, START, END
from chatbot.state_manager import GraphState
from .nodes.subquery import subquery_generate
from .nodes.intent_classifier import intent_classifier
from .nodes.account_summary_node import account_summary_node
from .nodes.balance_node import balance_node
from .nodes.final_result import final_result
from .nodes.get_operations import get_operations
from .nodes.numeric_pipeline import numeric_pipeline
from .nodes.visualize import visualize_pipeline
from .nodes.pick_subquery_node import pick_sub_query,increment_index
from .nodes.should_continue import should_continue
from .nodes.summary_results import summary_pipeline
from .nodes.transactions_summary import transaction_summary_node

from fastapi import APIRouter, Depends
from database import get_db
from oauth2 import get_current_user
from sqlalchemy.orm import Session
from models import User

router=APIRouter(
    tags=["chatbot"],
    prefix="/chat"
)






graph = StateGraph(GraphState)

# -------- Nodes --------
graph.add_node("decompose_query", subquery_generate)
graph.add_node("pick_sub_query", pick_sub_query)
graph.add_node("intent_classifier", intent_classifier)
graph.add_node("get_operations", get_operations)
graph.add_node("visualize_pipeline",visualize_pipeline)
graph.add_node("numeric_pipeline", numeric_pipeline)
graph.add_node("summary_pipeline", summary_pipeline)
graph.add_node("final_result", final_result)
graph.add_node("increment_index",increment_index)

# -------- Edges --------
graph.add_edge(START, "decompose_query")
graph.add_edge("decompose_query", "pick_sub_query")
graph.add_edge("pick_sub_query", "intent_classifier")

# Intent routing
graph.add_edge("intent_classifier", "get_operations")

graph.add_conditional_edges(
    "get_operations",
    lambda state: state["intent"],
    {
        "numeric": "numeric_pipeline",
        "visualize": "visualize_pipeline",
        "summary": "summary_pipeline"
    }
)



# Numeric path
graph.add_edge("numeric_pipeline", "final_result")

# Summary path
graph.add_edge("summary_pipeline", "final_result")
graph.add_edge("visualize_pipeline", "final_result")

graph.add_edge("final_result","increment_index")

# Loop control (NO should_continue node)
graph.add_conditional_edges(
    "increment_index",
    should_continue,   # decision function ONLY
    {
        "continue": "pick_sub_query",
        "stop": END
    }
)

final_graph=graph.compile()




@router.post("/chat")
def chat_endpoint(
    user_input: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    initial_state: GraphState = {
        "question": user_input,

        # decomposition
        "sub_queries": None,
        "current_sub_query": None,

        # loop
        "current_index": None,
        "results": None,

        # intent
        "intent": None,

        # numeric
        "operation": None,
        "params": {},
        "numeric_result": None,

        # summary
        "documents": None,
        "summary_result": None,

        # final
        "final_answer": None,

        # ✅ IMPORTANT PART
        "db": db,
        "user_id": current_user.id, #type:ignore
        "should_continue":None
    }

    result_state = final_graph.invoke(initial_state)

    return {
        "answer": result_state["results"]
    }
