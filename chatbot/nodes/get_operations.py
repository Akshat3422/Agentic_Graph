from utils import is_future_query,output_format
from schemas.chatbot.schema import OperationType,OperationParams
from chatbot.prompts.parameters import system_message
from langchain_core.prompts import ChatPromptTemplate
import os
from pydantic import BaseModel
from langchain_groq.chat_models import ChatGroq
from chatbot.state_manager import GraphState
from chatbot.operations import OPERATION_HANDLER_MAP
groq_api_key=os.getenv("GROQ_API_KEY")

model=ChatGroq(model="openai/gpt-oss-120b",api_key=groq_api_key) #type:ignore




class LLMStructuredOutput(BaseModel):
    operation: OperationType
    params: OperationParams



llm=model.with_structured_output(LLMStructuredOutput)


prompts=ChatPromptTemplate(
    messages=[
        system_message,
        ("human", "{user_input}")
    ]
)
chain=prompts|llm

def get_operations(state:GraphState) : #type: ignore
    question=str(state['current_sub_query'])
    if is_future_query(query=question):
        state["operation"] = None
        state["params"] = {}
        return state
    else:
        response=chain.invoke({"user_input":question})
        normal_response=output_format(response=response)
        if  normal_response['operation'] not in OPERATION_HANDLER_MAP:
            raise ValueError(f"Unsupported operation: {normal_response['operation'] }")

        state['operation']=normal_response['operation'] #type:ignore
        state['params']=normal_response['params']
        return state
