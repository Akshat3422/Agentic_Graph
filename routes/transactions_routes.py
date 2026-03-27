from fastapi import APIRouter, HTTPException,status, Depends
from pydantic import BaseModel
from models import Accounts, User,Transactions
from sqlalchemy.orm import Session
from database import get_db
from oauth2 import get_current_user
from schemas.transactions import TransactionModel,TransactionUpdate,TransactionType
from app_logger import setup_logging
from datetime import datetime, timezone

logger = setup_logging(__name__)


transaction_router=APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)



@transaction_router.post("/",status_code=status.HTTP_201_CREATED)
def create_transaction(
    account_id:int,
    transaction_details: TransactionModel,
    db:Session=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if not current_user.is_email_verified : # type: ignore
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Email not verified. Please verify your email to create an account.")

        account=db.query(Accounts).filter(Accounts.id==account_id,Accounts.user_id == current_user.id).first()

        if transaction_details.transaction_type.value == "income":
            account.balance += transaction_details.amount # type: ignore
        else:
            if account.balance < transaction_details.amount: # type: ignore
                logger.warning(f"Insufficient balance for expense: account_id={account_id}, user={current_user.username}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Insufficient balance for this expense transaction.")
            account.balance -= transaction_details.amount # type: ignore

        new_transaction = Transactions(
            account_id=account.id, # type: ignore
            transaction_type=transaction_details.transaction_type.value,
            amount=transaction_details.amount,
            description=transaction_details.description,
            category=transaction_details.category.value,
            timestamp=transaction_details.timestamp or datetime.now(timezone.utc),
        )
        db.add(new_transaction) # type: ignore
        db.commit() # type: ignore

        db.refresh(new_transaction) # type: ignore
        logger.info(f"Transaction created: id={new_transaction.id if hasattr(new_transaction, 'id') else 'n/a'} account_id={account_id} user={current_user.username} type={new_transaction.transaction_type} amount={new_transaction.amount}")
        return new_transaction
    except Exception as e:
        db.rollback()  # type: ignore
        logger.error(f"Error creating transaction for account_id={account_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@transaction_router.get("/{transaction_id}",status_code=status.HTTP_200_OK)
def get_transaction(
    transaction_id:int,
    db:Session=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction=db.query(Transactions).join(Accounts).filter(
        Transactions.id==transaction_id,
        Accounts.user_id==current_user.id
    ).first()

    if not transaction:
        logger.warning(f"Transaction not found: id={transaction_id} user={current_user.username}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Transaction not found.")

    logger.info(f"Transaction retrieved: id={transaction_id} user={current_user.username}")
    return transaction

@transaction_router.delete("/{transaction_id}",status_code=status.HTTP_200_OK)
def delete_transaction(
    transaction_id:int,
    db:Session=Depends(get_db),
    current_user: User = Depends(get_current_user)

):
    try:
        if not current_user.is_email_verified: #type:ignore
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="email not verified")

        transaction=db.query(Transactions).join(Accounts).filter(
            Transactions.id==transaction_id,
            Accounts.user_id==current_user.id
        ).first()

        if not transaction:
            logger.warning(f"Attempt to delete non-existent transaction id={transaction_id} by user {current_user.username}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Transaction not found.")

        # Adjust account balance
        account = (
            db.query(Accounts)
            .filter(Accounts.id == transaction.account_id)
            .with_for_update()
            .one()
        )

        # 1️⃣ Revert old transaction
        if transaction.transaction_type == "income": #type: ignore
            account.balance -= transaction.amount #type: ignore
        else:
            account.balance += transaction.amount #type: ignore
 

        db.flush()
        db.refresh(account) # type: ignore

        db.delete(transaction)
        db.commit() 
        logger.info(f"Transaction deleted: id={transaction_id} by user {current_user.username}")
        return {"detail":"Transaction deleted successfully."}
    except Exception as e:
        db.rollback()
        logger.exception(f"Eror deleting transaction id ={transaction_id}" )# type: ignore
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Internal Server Error")

# for getting all transactions of a particular account
@transaction_router.get("/account/{account_id}",status_code=status.HTTP_200_OK)
def get_account_transactions(
    account_id:int,
    db:Session=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account=db.query(Accounts).filter(
        Accounts.id==account_id,
        Accounts.user_id==current_user.id
    ).first()

    if not account:
        logger.warning(f"Account not found when listing transactions: id={account_id} user={current_user.username}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Account not found.")

    transactions=db.query(Transactions).filter(
        Transactions.account_id==account.id
    ).all() # type: ignore
    logger.info(f"Retrieved {len(transactions)} transactions for account_id={account_id} user={current_user.username}")
    return transactions

@transaction_router.put("/{transaction_id}",status_code=status.HTTP_200_OK)
def update_transaction(
    transaction_id: int,
    transaction_details: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if not current_user.is_email_verified:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified."
            )

        transaction = (
            db.query(Transactions)
            .join(Accounts)
            .filter(
                Transactions.id == transaction_id,
                Accounts.user_id == current_user.id
            )
            .first()
        )

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found."
            )

        # 🔒 Lock account row
        account = (
            db.query(Accounts)
            .filter(Accounts.id == transaction.account_id)
            .with_for_update()
            .one()
        )

        # 1️⃣ Revert old transaction
        if transaction.transaction_type == "income": #type: ignore
            account.balance -= transaction.amount #type: ignore
        else:
            account.balance += transaction.amount #type: ignore

        # 2️⃣ Determine new values
        new_amount = transaction_details.amount or transaction.amount
        new_type = (
            transaction_details.transaction_type.value
            if transaction_details.transaction_type
            else transaction.transaction_type
        )

        # 3️⃣ Apply new transaction
        if new_type == "income": #type: ignore
            account.balance += new_amount #type: ignore
        else:
            if account.balance < new_amount: #type: ignore
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient balance for this expense transaction."
                )
            account.balance -= new_amount #type: ignore

        # 4️⃣ Update transaction fields
        transaction.amount = new_amount #type: ignore
        transaction.transaction_type = new_type #type: ignore
        transaction.description = transaction_details.description or transaction.description #type: ignore

        if transaction_details.category:
            transaction.category = transaction_details.category.value #type: ignore

        if transaction_details.timestamp:
            transaction.timestamp = transaction_details.timestamp #type: ignore

        # 🔥 Force SQLAlchemy to track changes
        db.flush()

        db.commit()
        db.refresh(transaction)
        db.refresh(account)

        return transaction

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
