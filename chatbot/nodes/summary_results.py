from chatbot.nodes.account_summary_node import account_summary_node
from chatbot.nodes.balance_node import balance_node
from chatbot.nodes.transactions_summary import transaction_summary_node,get_expense_history_node,get_category_wise_expense
from chatbot.state_manager import GraphState
from chatbot.nodes.user_account_node import user_account_node
from chatbot.services.spending import top_category,total_spend_by_category
from chatbot.services.trend import compare_periods,spending_trends,monthly_summary
from schemas.chatbot.schema import OperationType



def monthly_summary_node(state: GraphState) -> GraphState:
    db = state["db"]
    params = state.get("params", {})

    result = monthly_summary(db, params)

    state["summary_result"] = result #type: ignore
    return state


def spending_trends_node(state: GraphState) -> GraphState:
    db = state["db"]
    params = state.get("params", {})

    result = spending_trends(db, params)

    state["summary_result"] = result #type: ignore
    return state

def compare_periods_node(state: GraphState) -> GraphState:
    db = state["db"]
    params = state.get("params", {})

    result = compare_periods(db, params)

    state["summary_result"] = result #type: ignore
    return state



def top_category_node(state: GraphState) -> GraphState:
    db = state["db"]
    params = state.get("params", {})

    result = top_category(db, params)

    state["summary_result"] = result #type: ignore
    return state

def total_spend_by_category_node(state: GraphState) -> GraphState:
    db = state["db"]
    params = state.get("params", {})

    result = total_spend_by_category(db, params)

    state["summary_result"] = result #type: ignore
    return state  




SUMMARY_NODE_MAP = {
    # --------------------
    # Account / User summaries
    # --------------------
    OperationType.User_Accounts: user_account_node,
    OperationType.Account_Summary: account_summary_node,

    # --------------------
    # Transaction summaries
    # --------------------
    OperationType.Recent_Operations: transaction_summary_node,

    # Spend
    OperationType.Top_Category: top_category_node,
    OperationType.Total_Spend_Category:total_spend_by_category_node,

    # --------------------
    # Time / trend summaries (optional)
    OperationType.Spending_Trends:compare_periods_node,
    OperationType.Monthly_Summary:monthly_summary_node,
    OperationType.Compose_Periods:compare_periods_node
    


}





def summary_pipeline(state: GraphState) -> GraphState:
    params = state.get("params") or {}
    

    # 🔑 Inject authenticated user_id
    params["user_id"] = state["user_id"]
    state["params"] = params

    operation = state["operation"]
    node = SUMMARY_NODE_MAP.get(operation) #type: ignore

    if not node:
        state["summary_result"] = "Unsupported summary request"
        return state

    return node(state)
