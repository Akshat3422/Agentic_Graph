from sqlalchemy.orm import Session
from models import Accounts,User


def current_balance(db: Session, params: dict):
    account_id=params.get("account_id")
    user_id = params.get("user_id")
    if not account_id or not user_id:
        return None

    account = (
        db.query(Accounts)
        .filter(
            Accounts.id == account_id,
            Accounts.user_id == user_id
        )
        .first()
    )
    if not account:
        return None

    return {
        "account_id": account.id,
        "balance": (account.balance)
    }


def balance_change(db: Session, params: dict):
    pass

