from chatbot.state_manager import GraphState


def pick_sub_query(state: GraphState) -> GraphState:
    idx = state.get("current_index")
    subq = state.get("sub_queries")

    if idx is None or not subq:
        state["current_sub_query"] = None
        return state

    # pick current subquery
    state["current_sub_query"] = subq[idx]

    return state

def increment_index(state: GraphState) -> GraphState:
    state["current_index"] += 1  # type: ignore
    return state

