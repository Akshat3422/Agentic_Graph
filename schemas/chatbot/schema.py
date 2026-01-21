from typing import Literal, Optional,Dict,Any
from pydantic import BaseModel,Field
from enum import Enum


from enum import Enum

class OperationType(str, Enum):
    # --------------------
    # Spending
    # --------------------
    Total_Spend = "Total_Spend"
    Total_Spend_Category = "Total_Spend_Category"
    Category_Break = "Category_Break"
    Top_Category = "Top_Category"
    Avg_Daily_Spend = "Avg_Daily_Spend"

    # --------------------
    # Income / Expense
    # --------------------
    Total_Income = "Total_Income"
    Total_Expense = "Total_Expense"

    # --------------------
    # Balance
    # --------------------
    Current_Balance = "Current_Balance"
    Balance_Change = "Balance_Change"

    # --------------------
    # Trends / Time
    # --------------------
    Spending_Trends = "Spending_Trends"
    Monthly_Summary = "Monthly_Summary"
    Compose_Periods = "Compose_Periods"

    # --------------------
    # Transactions
    # --------------------
    Recent_Operations = "Recent_Operations"
    Largest_Transactions = "Largest_Transactions"

    # --------------------
    # Summary / Fallback
    # --------------------
    Account_Summary = "Account_Summary"
    User_Accounts = "User_Accounts"
    Unsupported = "UNSUPPORTED"





class TimeRange(str, Enum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    LAST_30_DAYS = "last_30_days"
    CUSTOM = "custom"


class OperationParams(BaseModel):
    category: Optional[str] = Field(
        None,
        description="Expense or income category like food, travel, rent"
    )
    range: Optional[TimeRange] = None

    # Used only when range = custom
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    account_id: Optional[int] = None
    limit: Optional[int] = Field(
        None,
        ge=1,
        le=50,
        description="Limit for recent transactions"
    )

    period: Optional[str] = Field(
        None,
        description="daily / weekly / monthly"
    )

    metric: Optional[str] = Field(
        None,
        description="Metric like total_spent, total_income"
    )

    period_1: Optional[str] = None
    period_2: Optional[str] = None
    user_id:Optional[int]=None

