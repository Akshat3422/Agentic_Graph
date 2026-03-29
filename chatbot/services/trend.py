from datetime import datetime, timedelta, timezone

from sqlalchemy import case
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

from models import Accounts, TransactionType, Transactions
from utils import get_naive_time_range_bounds


def _normalize_period(value: str) -> str:
    if not value:
        return "daily"
    v = str(value).strip().lower()
    if v in {"day", "daily"}:
        return "daily"
    if v in {"week", "weekly"}:
        return "weekly"
    if v in {"month", "monthly"}:
        return "monthly"
    return v


def spending_trends(db: Session, params: dict):
    """
    Returns aggregated spending buckets over time.
    """
    account_id = params.get("account_id")
    user_id = params.get("user_id")
    if not account_id or not user_id:
        return []

    period = _normalize_period(params.get("period") or "daily")
    time_bounds = get_naive_time_range_bounds(params)
    now = datetime.now(timezone.utc)

    if time_bounds:
        start_utc, end_utc = time_bounds
    else:
        start_utc, end_utc = (now - timedelta(days=30), now)

    if period == "weekly":
        bucket = func.date_trunc("week", Transactions.timestamp)
    elif period == "monthly":
        bucket = func.date_trunc("month", Transactions.timestamp)
    else:
        bucket = func.date(Transactions.timestamp)

    rows = (
        db.query(
            bucket.label("bucket"),
            func.coalesce(func.sum(Transactions.amount), 0).label("total_amount"),
        )
        .join(Accounts, Accounts.id == Transactions.account_id)
        .filter(
            Transactions.account_id == account_id,
            Accounts.user_id == user_id,
            Transactions.transaction_type == TransactionType.EXPENSE,
            Transactions.timestamp >= start_utc,
            Transactions.timestamp <= end_utc,
        )
        .group_by(bucket)
        .order_by(bucket)
        .all()
    )

    return [{"period": str(r.bucket), "amount": float(r.total_amount)} for r in rows]


def monthly_summary(db: Session, params: dict):
    """
    Returns per-month income, expense, and net for the given account & range.
    """
    account_id = params.get("account_id")
    user_id = params.get("user_id")
    if not account_id or not user_id:
        return []

    time_bounds = get_naive_time_range_bounds(params)
    now = datetime.now(timezone.utc)

    if time_bounds:
        start_utc, end_utc = time_bounds
    else:
        start_utc, end_utc = (now - timedelta(days=180), now)

    bucket = func.date_trunc("month", Transactions.timestamp)

    income_sum = func.coalesce(
        func.sum(
            case(
                (Transactions.transaction_type == TransactionType.INCOME, Transactions.amount),
                else_=0,
            )
        ),
        0,
    )
    expense_sum = func.coalesce(
        func.sum(
            case(
                (Transactions.transaction_type == TransactionType.EXPENSE, Transactions.amount),
                else_=0,
            )
        ),
        0,
    )

    rows = (
        db.query(
            bucket.label("month"),
            income_sum.label("income"),
            expense_sum.label("expense"),
        )
        .join(Accounts, Accounts.id == Transactions.account_id)
        .filter(
            Transactions.account_id == account_id,
            Accounts.user_id == user_id,
            Transactions.timestamp >= start_utc,
            Transactions.timestamp <= end_utc,
        )
        .group_by(bucket)
        .order_by(bucket)
        .all()
    )

    return [
        {
            "month": str(r.month),
            "income": float(r.income),
            "expense": float(r.expense),
            "net": float(r.income) - float(r.expense),
        }
        for r in rows
    ]


def compare_periods(db: Session, params: dict):
    """
    Compares a metric across two named ranges (e.g. last_month vs this_month).
    """
    account_id = params.get("account_id")
    user_id = params.get("user_id")
    if not account_id or not user_id:
        return None

    period_1 = params.get("period_1")
    period_2 = params.get("period_2")
    if not period_1 or not period_2:
        return None

    metric = (params.get("metric") or "total_spent").lower()
    want_income = metric in {"total_income", "income", "total_income_spend"}
    want_net = metric in {"net", "net_balance", "net_balance_change"}

    if str(period_1).lower() == "custom" or str(period_2).lower() == "custom":
        return None

    b1 = get_naive_time_range_bounds({"range": period_1})
    b2 = get_naive_time_range_bounds({"range": period_2})
    if not b1 or not b2:
        return None

    start_1, end_1 = b1
    start_2, end_2 = b2

    def value_for_bounds(start_utc: datetime, end_utc: datetime) -> float:
        if want_net:
            income = (
                db.query(func.coalesce(func.sum(Transactions.amount), 0))
                .join(Accounts, Accounts.id == Transactions.account_id)
                .filter(
                    Transactions.account_id == account_id,
                    Accounts.user_id == user_id,
                    Transactions.transaction_type == TransactionType.INCOME,
                    Transactions.timestamp >= start_utc,
                    Transactions.timestamp <= end_utc,
                )
                .scalar()
            )
            expense = (
                db.query(func.coalesce(func.sum(Transactions.amount), 0))
                .join(Accounts, Accounts.id == Transactions.account_id)
                .filter(
                    Transactions.account_id == account_id,
                    Accounts.user_id == user_id,
                    Transactions.transaction_type == TransactionType.EXPENSE,
                    Transactions.timestamp >= start_utc,
                    Transactions.timestamp <= end_utc,
                )
                .scalar()
            )
            return float(income or 0.0) - float(expense or 0.0)

        txn_type = TransactionType.INCOME if want_income else TransactionType.EXPENSE
        val = (
            db.query(func.coalesce(func.sum(Transactions.amount), 0))
            .join(Accounts, Accounts.id == Transactions.account_id)
            .filter(
                Transactions.account_id == account_id,
                Accounts.user_id == user_id,
                Transactions.transaction_type == txn_type,
                Transactions.timestamp >= start_utc,
                Transactions.timestamp <= end_utc,
            )
            .scalar()
        )
        return float(val or 0.0)

    v1 = value_for_bounds(start_1, end_1)
    v2 = value_for_bounds(start_2, end_2)

    return {
        "period_1": str(period_1),
        "value_1": v1,
        "period_2": str(period_2),
        "value_2": v2,
        "difference": v2 - v1,
    }