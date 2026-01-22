from typing import TypedDict, Optional, Dict, Any, List,Literal
from sqlalchemy.orm import Session


from typing import TypedDict, Optional, Dict, Any, List
from sqlalchemy.orm import Session


class GraphState(TypedDict):
    # User input
    question: str

    # Decomposition
    sub_queries: Optional[List[str]]
    current_sub_query: Optional[str]

    # Loop control
    current_index: Optional[int]
    results: Optional[List[Dict[str, Any]]]

    # Intent
    intent: Optional[Literal["numeric","summary","visualize"]]  # 1 = numeric, 0 = summary

    # Numeric pipeline
    operation: Optional[str]
    params: Dict[str, Any]
    numeric_result: Optional[Any]

    # Summary / RAG
    documents: Optional[List[str]]
    summary_result: Optional[str]
    should_continue:Optional[str]
    visualize_result:Optional[List[Any]]

    # DB context
    db: Session
    user_id:Optional[int]

    # Final output
    final_answer: Optional[str]

