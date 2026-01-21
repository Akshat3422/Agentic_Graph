from chatbot.services.account_summary import get_balance_service
from chatbot.state_manager import GraphState




def balance_node(state: GraphState) -> GraphState:
    db = state["db"]
    user = state["user"]
    account_id = state["params"].get("account_id")

    balance = get_balance_service(db, user, account_id) #type: ignore
    state["summary_result"] = f"Your current balance is ₹{balance}"
    return state
