from chatbot.graph import final_graph
from database import get_db
from oauth2 import get_current_user
from chatbot.services.spending import total_spend_by_category,top_category

db = next(get_db())  # sync test ke liye

questions=[
    # "How much total money have I spent from account 7?",
    # "What is my total spend this month from account 7?",
    # "How much did I spend on food from account 7?",
    # "Which category has the highest spending in account 7?",
    # "What is my average daily spending from account 7?",
    # "What is my current balance in account 7?",
    "How much did I spend in the last 7 days from account 7?",
    # "Show me my recent transactions from account 7",
    # "What is my largest transaction in account 7?",
    # "How much income have I earned in account 7?",
    # "What is my total expense in account 7?",
    # "Compare my spending for last month and this month in account 7",
    # "Provide me the summary of total spend in each category  in the account 7?",
    # "What accounts do I have linked?",
    # "Show me summary for account 7"
]

answers=[]
for question in questions:
    initial_state = {
        # "question": "Where am I spending the most money in account id 7?",
        'question':question,
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
    answers.append(answer)



for answer in answers:
    print(f"\n{answer['final_answer']} \n")


print(answers[0])



