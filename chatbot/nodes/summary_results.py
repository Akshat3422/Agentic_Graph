from chatbot.nodes.account_summary_node import account_summary_node
from chatbot.nodes.balance_node import balance_node
from chatbot.nodes.transactions_summary import transaction_summary_node
from chatbot.state_manager import GraphState
from chatbot.nodes.user_account_node import user_account_node




from schemas.chatbot.schema import OperationType

SUMMARY_NODE_MAP = {
    # --------------------
    # Account / User summaries
    # --------------------
    OperationType.User_Accounts: user_account_node,
    OperationType.Account_Summary: account_summary_node,

    # --------------------
    # Balance summaries
    # --------------------
    OperationType.Current_Balance: balance_node,

    # --------------------
    # Transaction summaries
    # --------------------
    OperationType.Recent_Operations: transaction_summary_node,
    OperationType.Largest_Transactions: transaction_summary_node,

    # --------------------
    # Time / trend summaries (optional)
    # --------------------
    # OperationType.Monthly_Summary: monthly_summary_node,
    # OperationType.Spending_Trends: spending_trends_node,
}






def summary_pipeline(state: GraphState) -> GraphState:
    operation = state["operation"]

    node = SUMMARY_NODE_MAP.get(operation) #type: ignore
    if not node:
        state["summary_result"] = "Unsupported summary request"
        return state

    return node(state)
