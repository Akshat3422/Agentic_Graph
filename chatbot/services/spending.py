from models import Transactions, TransactionType, Accounts, ExpenditureCategory
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone, timedelta

from utils import get_utc_time_range_bounds

def total_spend_by_category(db: Session, params: dict):
    account_id = params.get("account_id")
    user_id = params.get("user_id")
    if not account_id or not user_id:
        return []

    time_bounds = get_utc_time_range_bounds(params)

    q = (
        db.query(
            Transactions.category,
            func.coalesce(func.sum(Transactions.amount), 0).label("total_amount"),
        )
        .join(Accounts, Accounts.id == Transactions.account_id)
        .filter(
            Transactions.account_id == account_id,
            Accounts.user_id == user_id,
            Transactions.transaction_type == TransactionType.EXPENSE,
        )
    )

    if params.get("category"):
        try:
            q = q.filter(Transactions.category == ExpenditureCategory(params["category"]))
        except Exception:
            # If the category is unknown to the enum, return empty results.
            return []

    if time_bounds:
        start_utc, end_utc = time_bounds
        q = q.filter(Transactions.timestamp >= start_utc, Transactions.timestamp <= end_utc)

    rows = q.group_by(Transactions.category).order_by(desc(func.sum(Transactions.amount))).all()

    return [
        {
            "category": row.category.value if row.category else "unknown",
            "amount": float(row.total_amount),
        }
        for row in rows
    ]


def category_break(db: Session, params: dict):
    account_id=params.get("account_id")
    user_id = params.get("user_id")

    q = (
        db.query(
            Transactions.category,
            func.sum(Transactions.amount).label("total_amount"),
        )
        .join(Accounts, Accounts.id == Transactions.account_id)
        .filter(
            Transactions.account_id == account_id,
            Transactions.transaction_type == TransactionType.EXPENSE,
        )
    )
    if user_id:
        q = q.filter(Accounts.user_id == user_id)

    summary = q.group_by(Transactions.category).all()

    return [
        {
            "category": row.category.value if row.category else "unknown",
            "amount": float(row.total_amount)
        }
        for row in summary
    ]



def top_category(db: Session, params: dict):
    account_id = params.get("account_id")
    user_id = params.get("user_id")
    if not account_id or not user_id:
        return None

    time_bounds = get_utc_time_range_bounds(params)

    q = (
        db.query(
            Transactions.category,
            func.coalesce(func.sum(Transactions.amount), 0).label("total_amount"),
        )
        .join(Accounts, Accounts.id == Transactions.account_id)
        .filter(
            Transactions.account_id == account_id,
            Accounts.user_id == user_id,
            Transactions.transaction_type == TransactionType.EXPENSE,
        )
    )

    if time_bounds:
        start_utc, end_utc = time_bounds
        q = q.filter(Transactions.timestamp >= start_utc, Transactions.timestamp <= end_utc)

    row = q.group_by(Transactions.category).order_by(desc(func.sum(Transactions.amount))).first()
    if not row:
        return None
    return {
        "category": row.category.value if row.category else "unknown",
        "amount": float(row.total_amount),
    }


def total_spend(db: Session, params: dict):
    account_id = params.get("account_id")
    user_id = params.get("user_id")
    if not account_id or not user_id:
        return 0.0

    time_bounds = get_utc_time_range_bounds(params)

    q = (
        db.query(func.coalesce(func.sum(Transactions.amount), 0))
        .join(Accounts, Accounts.id == Transactions.account_id)
        .filter(
            Transactions.account_id == account_id,
            Accounts.user_id == user_id,
            Transactions.transaction_type == TransactionType.EXPENSE,
        )
    )

    if time_bounds:
        start_utc, end_utc = time_bounds
        q = q.filter(Transactions.timestamp >= start_utc, Transactions.timestamp <= end_utc)

    total = q.scalar()
    return float(total or 0.0)


def average_daily_spend(db: Session, params: dict):
    account_id = params.get("account_id")
    user_id = params.get("user_id")
    if not account_id or not user_id:
        return 0.0

    time_bounds = get_utc_time_range_bounds(params)
    now = datetime.now(timezone.utc)

    # Default to a reasonable window if the model didn't provide one.
    if not time_bounds:
        start_utc = now - timedelta(days=30)
        end_utc = now
    else:
        start_utc, end_utc = time_bounds

    total_spent = total_spend(db, {**params, "account_id": account_id, "user_id": user_id})
    duration_days = max(1.0, (end_utc - start_utc).total_seconds() / 86400.0)
    return float(total_spent) / duration_days

    
