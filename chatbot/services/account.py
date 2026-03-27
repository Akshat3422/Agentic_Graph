from models import Accounts
from sqlalchemy.orm import Session



def get_user_accounts_service(db: Session, params: dict):
    user_id=params.get("user_id")
    return db.query(Accounts).filter(Accounts.user_id == user_id).all()


def get_account_details_service(db: Session, params: dict):
    account_id=params.get("account_id")
    user_id=params.get("user_id")
    return (
        db.query(Accounts)
        .filter(Accounts.id == account_id, Accounts.user_id == user_id)
        .first()
    )

def account_summary_handler(db, params):
    if params.get("account_id"):
        return get_account_details_service(db, params)
    else:
        return get_user_accounts_service(db, params)
