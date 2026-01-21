from chatbot.state_manager import GraphState
import os 
from dotenv import load_dotenv
from langchain_groq.chat_models import ChatGroq
from chatbot.prompts.parameters import answer_output_message
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()
groq_api_key=os.getenv("GROQ_API_KEY")
model=ChatGroq(model="openai/gpt-oss-120b",api_key=groq_api_key) #type: ignore

prompt = ChatPromptTemplate.from_messages([
    answer_output_message,
    ("human", 
     "User Query: {query}\n"
     "Numeric Result: {numeric_result}\n"
     "Summary Result: {summary_result}")
])

chain = prompt | model


def final_result(state: GraphState) -> GraphState:
    # Invoke LLM to synthesize final answer
    response = chain.invoke({
        "query": state.get("current_sub_query"),
        "numeric_result": state.get("numeric_result"),
        "summary_result": state.get("summary_result"),
    })

    # Extract content safely
    state["final_answer"] = response.content #type: ignore

    # Initialize results list if needed
    if state.get("results") is None:
        state["results"] = []

    # Safely append using a concrete string key
    sub_query = state["current_sub_query"]

    if state['results'] is not None:
        state['results'].append(
        {
            "question":str(sub_query),
            "answer":state['final_answer']
        }
    )
    # (Optional) reset per-subquery fields to avoid bleed into next loop
    state["numeric_result"] = None
    state["summary_result"] = None
    return state


