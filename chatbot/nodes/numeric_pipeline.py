from chatbot.state_manager import GraphState
from chatbot.operations import OPERATION_HANDLER_MAP
from schemas.chatbot.schema import OperationType




def numeric_pipeline(state: GraphState):
    operation = state["operation"]
    params = state.get("params") or {}
    db = state["db"]

    params["user_id"] = state["user_id"]

    handler = OPERATION_HANDLER_MAP.get(operation) #type: ignore
    if not handler:
        state["final_answer"] = f"Unsupported numeric operation: {operation}"
        return state

    result = handler(db, params)

    state["numeric_result"] = result
    state["final_answer"] = f"Result: {result}"

    return state


