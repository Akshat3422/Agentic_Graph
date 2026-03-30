from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime,timezone
from decimal import Decimal




class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"



class ExpenditureCategory(Enum):
    FOOD="food"
    SHOPPING="shopping"
    UTILITIES="utilities"
    ENTERTAINMENT="entertainment"
    TRANSPORTATION="transportation"
    OTHER="other"



class TransactionModel(BaseModel):
    transaction_type: TransactionType
    amount: Decimal
    description: str
    category: ExpenditureCategory
    timestamp:Optional[datetime] = None
    class Config:
        orm_mode = True


class TransactionOut(BaseModel):
    id: int
    amount: float
    transaction_type: str
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }

class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    category: Optional[ExpenditureCategory] = None
    transaction_type: Optional[TransactionType] = None
    timestamp:Optional[datetime]=None