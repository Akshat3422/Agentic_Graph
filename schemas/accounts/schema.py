from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import Enum
from decimal import Decimal


class AccountType(Enum):
    SAVINGS="savings"
    CHECKING="checking"
    CREDIT="credit" 

class CreateAccountRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_name: str
    account_type: AccountType
    balance: Optional[Decimal] = Decimal("0")
