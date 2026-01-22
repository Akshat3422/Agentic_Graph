from models import User,Transactions,TransactionType,Accounts
from sqlalchemy.sql import func
from sqlalchemy.orm import Session


from sqlalchemy.orm import Session



def total_spend_by_category(db: Session, params: dict):
    pass


def category_break(db: Session, params: dict):
    account_id=params.get("account_id")

    summary = (
        db.query(
            Transactions.category,
            func.sum(Transactions.amount).label("total_amount")
        )
        .filter(
            Transactions.account_id == account_id,
            Transactions.transaction_type == TransactionType.EXPENSE
        )
        .group_by(Transactions.category)
        .all()
    )

    return [
        {
            "category": row.category.value if row.category else "unknown",
            "amount": float(row.total_amount)
        }
        for row in summary
    ]



def top_category(db: Session, params: dict):
    pass


def total_spend(db: Session, params: dict):
    pass


def average_daily_spend(db: Session, params: dict):
    pass

    
