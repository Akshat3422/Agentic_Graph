from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime,timezone




class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"



class ExpenditureCategory(Enum):
    FOOD="food"
    UTILITIES="utilities"
    ENTERTAINMENT="entertainment"
    TRANSPORTATION="transportation"
    OTHER="other"



class TransactionModel(BaseModel):
    transaction_type: TransactionType
    amount: int
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
    amount: Optional[int] = None
    description: Optional[str] = None
    category: Optional[ExpenditureCategory] = None
    transaction_type: Optional[TransactionType] = None
    timestamp:Optional[datetime]=None