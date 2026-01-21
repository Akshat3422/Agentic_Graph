from fastapi import APIRouter, HTTPException,status, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from oauth2 import get_current_user
from models import Transactions, User, Accounts
from schemas.accounts.schema import AccountType,CreateAccountRequest
from schemas.transactions.schema import TransactionModel, TransactionOut
from datetime import datetime,timezone

account_router=APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)

from app_logger import setup_logging

logger = setup_logging(__name__)

@account_router.post("/",status_code=status.HTTP_201_CREATED)
def create_account(account_details: CreateAccountRequest,
                   initial_transaction: TransactionModel,
                   db:Session=Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    try:
        if not current_user.is_email_verified : # type: ignore
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Email not verified. Please verify your email to create an account.")
        account_count = db.query(Accounts).filter(
        Accounts.user_id == current_user.id
).count()
        if account_count>=3:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Account Already Exists")
        # 1️⃣ Create account with ZERO balance
        new_account = Accounts(
            account_name=account_details.account_name,
            account_type=account_details.account_type.value,
            balance=0,  
            user_id=current_user.id,
        )

        db.add(new_account) # type: ignore
        db.flush()  # type: ignore


        #  Create initial transaction (INCOME)
        new_transaction = Transactions(
            account_id=new_account.id,
            transaction_type=initial_transaction.transaction_type.value,
            amount=initial_transaction.amount,
            description=initial_transaction.description,
            category=initial_transaction.category.value,
            timestamp=initial_transaction.timestamp or datetime.now(timezone.utc)
        )

        # 3️⃣ Update balance based on transaction type
        if initial_transaction.transaction_type.value == "income":
            new_account.balance += initial_transaction.amount # type: ignore
        else:
            raise ValueError("Initial balance must be an INCOME transaction")
    # raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="account already exists")


        db.add(new_transaction)  # type: ignore

        # Single commit
        db.commit() # type: ignore

        db.refresh(new_account)# type: ignore

        logger.info(f"Account created: {new_account.account_name} (id={new_account.id}) for user {current_user.username}")

        return new_account
    except HTTPException:
        db.rollback()
        raise


    except Exception as e:
        db.rollback()  # type: ignore
        logger.error(f"Error creating account (commit): {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Internal Server Error ")



# For getting all accounts of the current user no parameters needed because we get user from token and also get_user dependency ensures the current user is valid
@account_router.get("/",status_code=status.HTTP_200_OK)
def get_user_accounts(db:Session=Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    if not current_user.is_email_verified : # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Email not verified. Please verify your email to create an account.")
    try:
        accounts = db.query(Accounts).filter(Accounts.user_id == current_user.id).all() # type: ignore
        logger.info(f"Retrieved {len(accounts)} accounts for user {current_user.username}")
        return accounts
    except Exception as e:
        logger.error(f"Error retrieving accounts for user {current_user.username}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))




# For Single account details including transactions
@account_router.get("/{account_id}",status_code=status.HTTP_200_OK)
def get_account_details(account_id:int,
                        db:Session=Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    try:
        if not current_user.is_email_verified : # type: ignore
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Email not verified. Please verify your email to create an account.")
        account = db.query(Accounts).filter(Accounts.id == account_id, Accounts.user_id == current_user.id).first() # type: ignore
        if not account:
            logger.warning(f"Account not found: id={account_id} for user {current_user.username}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Account not found")

        logger.info(f"Account details retrieved: id={account_id} for user {current_user.username}")
        return account
    except Exception as e:
        logger.error(f"Error retrieving account details id={account_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))






@account_router.get("/summary/{account_id}", status_code=status.HTTP_200_OK)
def get_account_summary(
    account_id:int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if not current_user.is_email_verified : # type: ignore
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Email not verified. Please verify your email to create an account.")
        account = db.query(Accounts).filter(
            Accounts.id == account_id,
            Accounts.user_id == current_user.id
        ).first()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        income_sum = db.query(func.coalesce(func.sum(Transactions.amount), 0)).filter( # type: ignore
            Transactions.account_id == account.id,
            Transactions.transaction_type == "income"
        ).scalar()

        expense_sum = db.query(func.coalesce(func.sum(Transactions.amount), 0)).filter( # type: ignore
            Transactions.account_id == account.id,
            Transactions.transaction_type == "expense"
        ).scalar()

        last_transactions = db.query(Transactions).filter( # type: ignore
            Transactions.account_id == account.id
        ).order_by(Transactions.timestamp.desc()).limit(5).all()

        #  Return summary
        logger.info(f"Account summary retrieved: id={account_id} for user {current_user.username}")
        return {
            "account_id": account.id,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "current_balance": account.balance,
            "total_income": income_sum,
            "total_expense": expense_sum,
            "net_balance": income_sum - expense_sum,
            "last_transactions": [TransactionOut.from_orm(t) for t in last_transactions]
        }
    except Exception as e:
        logger.error(f"Error retrieving account summary id={account_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# For balance Query 
@account_router.get("/summmary/{account_id}/balance",status_code=status.HTTP_302_FOUND)
def get_balancedirectly(
    account_id:int,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    try:
        if not current_user.is_email_verified : # type: ignore
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Email not verified. Please verify your email to create an account.")
        
        account=db.query(Accounts).filter(Accounts.id==account_id,
                                         Accounts.user_id== current_user.id).first()
        logger.info(f"Balance requested for account id={account_id} by user {current_user.username}")
        return f"The net balance associated with this account is {account.balance}" #type: ignore
    except Exception as e:
        logger.error(f"Error fetching balance for account id={account_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


# We are hard deleting the account here 
@account_router.delete('/delete/{account_id}',status_code=status.HTTP_200_OK)
def delete_user(
    account_id:int,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    try:
        if not current_user.is_email_verified: #type:ignore
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Email not verified ,Please verify your email to crete account")
        account=db.query(Accounts).filter(Accounts.id==account_id,
                                          Accounts.user_id==current_user.id).first()
        if not account:
            logger.warning(f"Attempted delete of non-existent account id={account_id} by user {current_user.username}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        
        
        db.query(Transactions).filter(
            Transactions.account_id == account_id
        ).delete(synchronize_session=False)

        db.delete(account) #type:ignore
        db.commit() #type:ignore\
        logger.info(f"Account deleted: id={account_id} by user {current_user.username}")
        return {"detail":f"The account with id {account_id} has been deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="unexpected occurence")






