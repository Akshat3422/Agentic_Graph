from sqlalchemy.orm import Session
from models import Accounts,User,Transactions
from chatbot.services.income import total_income_spend,total_expense


def current_balance(db: Session, params: dict):
    account_id = params.get("account_id")
    user_id = params.get("user_id")

    if not account_id or not user_id:
        return 0.0

    account = (
        db.query(Accounts)
        .filter(
            Accounts.id == account_id,
            Accounts.user_id == user_id
        )
        .first()
    )

    if not account:
        return 0.0

    return float(account.balance) #type: ignore



def balance_change(db: Session, params: dict):
    print(params)
    account_id = params.get("account_id")
    user_id = params.get("user_id")

    if not account_id or not user_id:
        return 0.0

    income = total_income_spend(db, params)
    expense = total_expense(db, params)

    # difference = income - expense
    return float(income or 0) - float(expense or 0)


