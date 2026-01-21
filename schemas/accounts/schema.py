from pydantic import BaseModel
from typing import Optional
from enum import Enum


class AccountType(Enum):
    SAVINGS="savings"
    CHECKING="checking"
    CREDIT="credit" 

class CreateAccountRequest(BaseModel):
    account_name: str
    account_type: AccountType  # Could be 'savings', 'checking', 'credit', etc.
    balance: Optional[int] = 0

    class Config:
        orm_mode = True
