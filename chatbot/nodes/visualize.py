from schemas.chatbot.schema import OperationType
from chatbot.state_manager import GraphState

from chatbot.nodes.transactions_summary import get_expense_history_node,get_category_wise_expense

VISUALIZE_NODE_MAP = {
    OperationType.VISUALIZE_EXPENSE_AND_INCOME: get_expense_history_node,
    OperationType.CATEGORY_WISE_VISUALIZE: get_category_wise_expense,
}


def visualize_pipeline(state: GraphState) -> GraphState:
    operation = state["operation"]

    node = VISUALIZE_NODE_MAP.get(operation) #type: ignore
    if not node:
        state["final_answer"] = f"Unsupported visualize request: {operation}"
        return state

    return node(state)
 


