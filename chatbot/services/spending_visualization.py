from models import User,Transactions,TransactionType,Accounts
from fastapi import APIRouter,Depends
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from database import get_db
from oauth2 import get_current_user



def get_transaction_type_summary(db: Session, account_id: int):
    summary = (
        db.query(
            Transactions.transaction_type,
            func.sum(Transactions.amount).label("total_amount")
        )
        .filter(Transactions.account_id == account_id)
        .group_by(Transactions.transaction_type)
        .all()
    )

    if not summary:
        return []

    return [
        {
            "transaction_type": row.transaction_type.value,
            "amount": float(row.total_amount)
        }
        for row in summary
    ]


def category_pie(db: Session, account_id: int):
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
