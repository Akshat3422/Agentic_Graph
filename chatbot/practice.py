from chatbot.graph import final_graph
from database import get_db
from oauth2 import get_current_user

db = next(get_db())  # sync test ke liye

initial_state = {
    # "question": "Where am I spending the most money in account id 7?",
     'question':"Show all my accounts",
    #  "Show my recent transactions for account id 7",
    "operation": None,
    "params": {},
    "numeric_result": None,
    "summary_result": None,
    "final_answer": None,
    "db": db,
    "user_id":4
}

answer = final_graph.invoke(initial_state) #type:ignore

print("RAW OPERATION FROM LLM:", answer["operation"])

print(answer)



