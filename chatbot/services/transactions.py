from sqlalchemy.orm import Session
from models import Transactions, Accounts

from utils import get_utc_time_range_bounds




def recent_operations(db: Session, params: dict):
    account_id = params.get("account_id")
    user_id = params.get("user_id")
    if not account_id or not user_id:
        return []

    limit = params.get("limit") or 10
    time_bounds = get_utc_time_range_bounds(params)

    q = (
        db.query(Transactions)
        .join(Accounts, Accounts.id == Transactions.account_id)
        .filter(
            Transactions.account_id == account_id,
            Accounts.user_id == user_id,
        )
        .order_by(Transactions.timestamp.desc())
        .limit(int(limit))
    )

    if time_bounds:
        start_utc, end_utc = time_bounds
        q = q.filter(Transactions.timestamp >= start_utc, Transactions.timestamp <= end_utc)

    rows = q.all()
    return [
        {
            "id": t.id,
            "transaction_type": t.transaction_type.value if t.transaction_type else None,
            "amount": float(t.amount),
            "description": t.description,
            "category": t.category.value if t.category else None,
            "timestamp": t.timestamp.isoformat() if t.timestamp else None,
        }
        for t in rows
    ]


def largest_transaction(db: Session, params: dict):
    account_id = params.get("account_id")
    user_id = params.get("user_id")
    if not account_id or not user_id:
        return []

    limit = params.get("limit") or 5
    time_bounds = get_utc_time_range_bounds(params)

    q = (
        db.query(Transactions)
        .join(Accounts, Accounts.id == Transactions.account_id)
        .filter(
            Transactions.account_id == account_id,
            Accounts.user_id == user_id,
        )
        .order_by(Transactions.amount.desc())
        .limit(int(limit))
    )

    if time_bounds:
        start_utc, end_utc = time_bounds
        q = q.filter(Transactions.timestamp >= start_utc, Transactions.timestamp <= end_utc)

    rows = q.all()
    return [
        {
            "id": t.id,
            "transaction_type": t.transaction_type.value if t.transaction_type else None,
            "amount": float(t.amount),
            "description": t.description,
            "category": t.category.value if t.category else None,
            "timestamp": t.timestamp.isoformat() if t.timestamp else None,
        }
        for t in rows
    ]



def get_account_transactions_service(db: Session, params: dict):
    account_id = params.get("account_id") if isinstance(params, dict) else params
    return db.query(Transactions).filter(
        Transactions.account_id == account_id
    ).all()