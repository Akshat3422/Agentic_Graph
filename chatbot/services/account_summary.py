from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Accounts, Transactions


def get_account_summary_service(db: Session, params: dict):
    
    print("DEBUG params:", params)  
    account_id=params.get("account_id")
    user_id=params.get("user_id")
    account = (
        db.query(Accounts)
        .filter(Accounts.id == account_id, Accounts.user_id == user_id)
        .first()
    )
    if not account:
        return None

    income = db.query(func.coalesce(func.sum(Transactions.amount), 0)).filter(
        Transactions.account_id == account.id,
        Transactions.transaction_type == "income"
    ).scalar()

    expense = db.query(func.coalesce(func.sum(Transactions.amount), 0)).filter(
        Transactions.account_id == account.id,
        Transactions.transaction_type == "expense"
    ).scalar()

    last_txns = (
        db.query(Transactions)
        .filter(Transactions.account_id == account.id)
        .order_by(Transactions.timestamp.desc())
        .limit(10)
        .all()
    )

    return {
        "account": account,
        "income": income,
        "expense": expense,
        "balance": account.balance,
        "last_transactions": last_txns,
    }


def get_balance_service(db: Session, params: dict):
    account_id=params.get("account_id")
    user_id=params.get("user")
    account = (
        db.query(Accounts)
        .filter(Accounts.id == account_id, Accounts.user_id == user_id)
        .first()
    )
    return account.balance if account else None


