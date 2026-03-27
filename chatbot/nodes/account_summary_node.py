from chatbot.state_manager import GraphState
from chatbot.services.account_summary import get_account_summary_service


def account_summary_node(state: GraphState) -> GraphState:
    db = state["db"]

    # ✅ pass params dict, not individual keywords
    summary = get_account_summary_service(
        db,
        state["params"]
    )

    if not summary:
        state["summary_result"] = "Account not found"
        return state

    state["summary_result"] = (
        f"Account balance is ₹{summary['balance']}. "
        f"Total income ₹{summary['income']} and expense ₹{summary['expense']}."
    )

    return state





