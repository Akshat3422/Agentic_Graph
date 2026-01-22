from ...models import User,Transactions,TransactionType,Accounts
import matplotlib.pyplot as plt #type: ignore 
from fastapi import APIRouter,Depends
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from database import get_db
from oauth2 import get_current_user


router=APIRouter(
    tags=["Transaction_Type"]
)

@router.get("/accounts/{account_id}/transactions/category-pie")
def get_transaction_type_summary(account_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    summary=db.query(
            Transactions.transaction_type,
            func.sum(Transactions.amount).label("total_amount")
    ).filter(
        Transactions.account_id==account_id
    ).group_by(Transactions.transaction_type).all()

    if not summary:
        return []

    return [
        {
            "transaction_type": tx.transaction_type.value,
            "amount": float(tx.total_amount)
        }
        for tx in summary
    ]



@router.get("/accounts/{account_id}/transactions/category-pie")
def category_pie(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
