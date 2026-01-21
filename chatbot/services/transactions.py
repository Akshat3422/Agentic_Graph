from sqlalchemy.orm import Session
from models import Transactions




def recent_operations(db: Session, params: dict):
    pass


def largest_transaction(db: Session, params: dict):
    pass



def get_account_transactions_service(db: Session, params: dict):
    account_id=params.get("account_id")
    return db.query(Transactions).filter(
        Transactions.account_id == account_id
    ).all()