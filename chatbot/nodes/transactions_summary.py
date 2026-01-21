from chatbot.state_manager import GraphState
from chatbot.services.transactions import get_account_transactions_service



def transaction_summary_node(state: GraphState) -> GraphState:
    db = state["db"]
    account_id = state["params"].get("account_id")

    txns = get_account_transactions_service(db, account_id) #type: ignore

    state["summary_result"] = f"You have {len(txns)} transactions in this account."
    return state
