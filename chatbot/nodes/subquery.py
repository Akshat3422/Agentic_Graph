from chatbot.state_manager import GraphState
from dotenv import load_dotenv
from langchain_groq.chat_models import ChatGroq
import os
from chatbot.prompts.parameters import decomposition_message
from langchain_core.prompts import ChatPromptTemplate
from utils import extract_sub_query




groq_api_key=os.getenv("GROQ_API_KEY")
model=ChatGroq(model="openai/gpt-oss-120b",api_key=groq_api_key) #type: ignore



prompt = ChatPromptTemplate(
	messages=[
		decomposition_message,
		("human", "{user_query}")
	]
)

decomposition_chain = prompt | model


def subquery_generate(state: GraphState) -> GraphState:
    response = decomposition_chain.invoke({
        "user_query": str(state["question"])
    })

    sub_queries = extract_sub_query(
        response.content if hasattr(response, "content") else response
    )

    state["sub_queries"] = sub_queries
    state["current_index"] = 0

    if sub_queries:
        state["current_sub_query"] = sub_queries[0]
    else:
        state["current_sub_query"] = None

    return state



