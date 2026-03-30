from ..state_manager import GraphState



def pick_expanded_query(state: GraphState) -> GraphState:
    idx = state.get("expanded_index", 0)
    queries = state.get("expanded_queries", [])
 
    if idx >= len(queries):  # type: ignore
        # state["expanded_done"] = True
        return state

    state["current_sub_query"] = queries[idx] # type: ignore
    state["expanded_index"] = idx + 1 # type: ignore
    # state["expanded_done"] = False

    return state

def increment_expanded_index(state: GraphState) -> GraphState:
    state["expanded_index"] += 1  # type: ignore
    return state