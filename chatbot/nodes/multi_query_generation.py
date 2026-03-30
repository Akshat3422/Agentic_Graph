from ..state_manager  import GraphState
from dotenv import load_dotenv
from typing import List
import os
from pydantic import BaseModel
from langchain_groq.chat_models import ChatGroq


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY") #type: ignore
load_dotenv()


model=ChatGroq(model="llama-3.3-70b-versatile")

class MultiQueryGenerationNode(BaseModel):
    output: List[str]

llm=model.with_structured_output(MultiQueryGenerationNode)


import json

def multi_query_generation(state: GraphState):
    sub_query = state.get("current_sub_query")

    if not sub_query:
        state["final_answer"] = "No sub-query provided."
        return state

    prompt = f"""
Break the user query into multiple distinct intents and generate exactly 5 queries.

Each query must:
- Be a complete standalone question
- Target a different intent
- Maximize retrieval diversity

Return ONLY valid JSON:
{{
  "queries": ["...", "..."]
}}

Query: {sub_query}
"""

    response = llm.invoke(prompt)

    try:
        parsed = json.loads(response.output)
        queries = parsed.get("queries", [])
    except:
        queries = [sub_query]

    # ✅ include original query
    all_queries = [sub_query] + queries

    # ✅ store properly
    state["expanded_queries"] = all_queries

    # ✅ initialize loop
    state["expanded_index"] = 0
    # state["results"] = []

    return state



