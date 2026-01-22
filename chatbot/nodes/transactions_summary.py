from chatbot.state_manager import GraphState
from chatbot.services.transactions import get_account_transactions_service
from chatbot.services.spending_visualization import get_transaction_type_summary,category_pie



def transaction_summary_node(state: GraphState) -> GraphState:
    db = state["db"]
    account_id = state["params"].get("account_id")

    txns = get_account_transactions_service(db, account_id) #type: ignore

    state["summary_result"] = f"You have {len(txns)} transactions in this account."
    return state


def get_expense_history_node(state: GraphState):
    db = state["db"]
    account_id = state["params"].get("account_id")

    answers = get_transaction_type_summary(db, account_id) #type: ignore

    state["visualize_result"] = answers
    state["final_answer"] = "Here is your expense vs income visualization."

    return state






def get_category_wise_expense(state: GraphState):
    db = state["db"]
    account_id = state["params"].get("account_id")

    answers = category_pie(db, account_id) #type: ignore

    state["visualize_result"] = answers
    state["final_answer"] = "Here is your category-wise expense visualization."

    return state
