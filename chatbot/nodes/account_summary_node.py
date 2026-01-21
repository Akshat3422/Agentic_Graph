from chatbot.state_manager import GraphState
from chatbot.services.account_summary import get_account_summary_service


def account_summary_node(state: GraphState) -> GraphState:
    db = state["db"]
    user = state["user"]
    account_id = state["params"].get("account_id")

    summary = get_account_summary_service(
        db=db,
        user_id=user, #type:ignore
        account_id=account_id  #type:ignore
    )

    if not summary:
        state["summary_result"] = "Account not found"
        return state

    state["summary_result"] = (
        f"Account balance is ₹{summary['balance']}. "
        f"Total income ₹{summary['income']} and expense ₹{summary['expense']}."
    )
    return state




