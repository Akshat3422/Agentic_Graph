from chatbot.state_manager import GraphState
from chatbot.operations import OPERATION_HANDLER_MAP
from schemas.chatbot.schema import OperationType




def numeric_pipeline(state: GraphState):
    operation = state["operation"]
    params = state.get("params") or {}
    db = state["db"]

    # 🔑 Inject authenticated user_id
    user_id = state["user_id"]
    params["user_id"] = user_id

    if operation not in OPERATION_HANDLER_MAP:
        raise ValueError(f"Unsupported operation: {operation}")

    handler = OPERATION_HANDLER_MAP[operation] #type:ignore

    state["numeric_result"] = handler(db, params)
    return state

