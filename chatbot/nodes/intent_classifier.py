from chatbot.prompts.parameters import intention_system_message
from langchain_groq.chat_models import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
from chatbot.state_manager import GraphState



load_dotenv()

groq_api_key=os.getenv("GROQ_API_KEY")
model=ChatGroq(model="openai/gpt-oss-120b",api_key=groq_api_key) #type: ignore

prompt=ChatPromptTemplate(
    messages=[
        intention_system_message,
        ("human", "{user_query}")
    ]
)

chain=prompt|model

def intent_classifier(state: GraphState):
    current_query=state['current_sub_query']
    response=chain.invoke({"user_query":current_query})
    raw = response.content.strip()  #type:ignore
# ✅ strict normalization
    if raw == "1":
        state["intent"] = 1
    else:
        state["intent"] = 0
    return state





