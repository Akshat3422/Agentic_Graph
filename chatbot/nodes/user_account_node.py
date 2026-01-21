from chatbot.services.account import get_user_accounts_service
from chatbot.state_manager import GraphState



def user_account_node(state: GraphState) -> GraphState:
    db = state["db"]
    user_id = state["user_id"]          # injected by auth
    params = {
        "user_id": user_id        # ✅ primitive
    }

    accounts = get_user_accounts_service(
        db,
        {"user_id": user_id}
    )
    state["summary_result"] = [ #type: ignore

        {
            "id": acc.id,
            "account_name": acc.account_name,
            "balance": acc.balance,
            "account_type": acc.account_type,
        }
        for acc in accounts
    ]
    return state
