from chatbot.graph import final_graph
from database import get_db
from oauth2 import get_current_user
from chatbot.services.spending import total_spend_by_category,top_category,total_spend
from utils import get_naive_time_range_bounds

db = next(get_db())  # sync test ke liye

questions=[
    # "How much total money have I spent from account 1?",
    # "What is my total spend this month from account 1?",
    # "How much did I spend on food from account 1?",
    # "Which category has the highest spending in account 1?",
    # "What is my average daily spending from account 1?",
    # "What is my current balance in account 1?",
    # "How much did I spend in the last 7 days from account 1?",
    # "Show me my recent transactions from account 1",
    # "What is my largest transaction in account 1?",
    # "How much income have I earned in account 1?",
    # "What is my total expense in account 1?",
    # "Compare my spending for last month and this month in account 1",
    # "Provide me the summary of total spend in each category  in the account 1?",
    # "What accounts do I have linked?",
    # "Show me summary for account 1"
    "Compare the balances of accounts with IDs 1, 2, and 3?"
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
        "user_id":1
    }

    answer = final_graph.invoke(initial_state) #type:ignore
    answers.append(answer)



for answer in answers:
    print(f"\n{answer['final_answer']} \n")


print(answers[0])


# params={"account_id":1,
#         "user_id":1,
#         "category":"food"
#         }
# time_bounds = total_spend_by_category(db,params=params)
# print(time_bounds)

