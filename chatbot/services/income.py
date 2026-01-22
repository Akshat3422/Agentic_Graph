from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models import User,Transactions,Accounts


def total_income_spend(db: Session, params: dict):
    print(params)
    account_id = params.get("account_id")
    user_id = params.get("user_id")

    if not account_id or not user_id:
        return 0.0

    total_income = (
        db.query(func.coalesce(func.sum(Transactions.amount), 0))
        .join(Accounts, Accounts.id == Transactions.account_id)
        .filter(
            Transactions.account_id == account_id,
            Accounts.user_id == user_id,
            Transactions.transaction_type == "income"
        )
        .scalar()
    )

    return float(total_income)




def total_expense(db: Session, params: dict):
    account_id = params.get("account_id")
    user_id = params.get("user_id")

    if not account_id or not user_id:
        return 0.0

    total = (
        db.query(
            func.coalesce(func.sum(Transactions.amount), 0)
        )
        .join(
            Accounts, Accounts.id == Transactions.account_id
        )
        .filter(
            Transactions.account_id == account_id,
            Transactions.transaction_type == "expense",
            Accounts.user_id == user_id
        )
        .scalar()
    )

    return float(total)
