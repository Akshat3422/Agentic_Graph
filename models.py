from database import Base
from sqlalchemy.orm import relationship,validates
from sqlalchemy import Column,Integer,Boolean,Text,String,Enum as SQLEnum,ForeignKey,DateTime,CheckConstraint, UniqueConstraint,Numeric
from enum import Enum
from sqlalchemy.sql import func
from datetime import datetime, timezone



class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True)
    username=Column(String(50),unique=True,nullable=False)
    email=Column(String(100),unique=True,nullable=False)
    password=Column(Text,nullable=False)
    is_active=Column(Boolean,default=True)
    is_email_verified = Column(Boolean, default=False)
    email_otp = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    accounts=relationship("Accounts",back_populates="user",cascade="all, delete-orphan")



class AccountType(Enum):
    SAVINGS="savings"
    CHECKING="checking"
    CREDIT="credit"                       


class Accounts(Base):
    __tablename__="accounts"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_balance_positive"),
        UniqueConstraint('user_id', 'account_type', name='uix_user_accounttype'),
    )
    id=Column(Integer,primary_key=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    account_name=Column(String(100),nullable=False)
    balance = Column(Numeric(12, 2), default=0)

    account_type=Column(SQLEnum(
        AccountType,
        values_callable=lambda enum: [e.value for e in enum],
        name="accounttype"
    )
    ,nullable=False,default=AccountType.SAVINGS.value)
    user=relationship("User",back_populates="accounts")
    transactions=relationship("Transactions",back_populates="account",cascade="all, delete-orphan")


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"



class ExpenditureCategory(Enum):
    FOOD="food"
    UTILITIES="utilities"
    ENTERTAINMENT="entertainment"
    TRANSPORTATION="transportation"
    OTHER="other"




class Transactions(Base):
    __tablename__ = "transactions"

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_amount_positive"),
    )

    id = Column(Integer, primary_key=True)

    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)

    transaction_type = Column(
        SQLEnum(
            TransactionType,
            values_callable=lambda enum: [e.value for e in enum],
            name="transactiontype"
        ),
        nullable=False,
        default=TransactionType.EXPENSE
    )

    amount = Column(Numeric(12, 2), nullable=False)

    description = Column(Text)

    timestamp = Column(
        DateTime,
        # server_default=func.now(), #only database has access
        default=datetime.now(timezone.utc),
        nullable=False
    )

    category = Column(
        SQLEnum(
            ExpenditureCategory,
            values_callable=lambda enum: [e.value for e in enum],
            name="expenditurecategory"
        ),
        nullable=True,
        default=ExpenditureCategory.OTHER
    )

    account = relationship("Accounts", back_populates="transactions")