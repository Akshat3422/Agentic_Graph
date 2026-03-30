from chatbot.state_manager import GraphState

def should_continue(state: GraphState) -> str:
    idx = state.get("current_index")
    subq = state.get("sub_queries")

    if idx is None or not subq:
        return "stop"

    if idx < len(subq):
        return "continue"

    return "stop"


def should_continue_inner(state: GraphState) -> str:
    idx = state.get("expanded_index", 0)
    queries = state.get("expanded_queries", [])

    if idx < len(queries):
        return "continue_inner"
    
    return "outer"