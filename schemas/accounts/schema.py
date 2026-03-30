from pydantic import BaseModel
from typing import Optional
from enum import Enum
from decimal import Decimal


class AccountType(Enum):
    SAVINGS="savings"
    CHECKING="checking"
    CREDIT="credit" 

class CreateAccountRequest(BaseModel):
    account_name: str
    account_type: AccountType  # Could be 'savings', 'checking', 'credit', etc.
    balance: Optional[Decimal] = Decimal("0")

    class Config:
        orm_mode = True
