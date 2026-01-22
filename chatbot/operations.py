from chatbot.services.spending import (
    total_spend,
    total_spend_by_category,
    category_break,
    top_category,
    average_daily_spend,
)

from chatbot.services.balance import (
    current_balance,
    balance_change,
)

from chatbot.services.income import (
    total_income_spend,
    total_expense,
)

from chatbot.services.transactions import (
    recent_operations,
    largest_transaction,
)

from chatbot.services.trend import (
    spending_trends,
    monthly_summary,
    compare_periods,
)
from chatbot.services.spending_visualization import get_transaction_type_summary,category_pie

from chatbot.services.account import account_summary_handler,get_user_accounts_service
from schemas.chatbot.schema import OperationType

OPERATION_HANDLER_MAP = {
    # --------------------
    # Spending
    # --------------------
    OperationType.Total_Spend: total_spend,
    OperationType.Total_Spend_Category: total_spend_by_category,
    OperationType.Top_Category: top_category,
    OperationType.Avg_Daily_Spend: average_daily_spend,

    # --------------------
    # Income / Expense
    # --------------------
    OperationType.Total_Income: total_income_spend,
    OperationType.Total_Expense: total_expense,

    # --------------------
    # Balance
    # --------------------
    OperationType.Current_Balance: current_balance,
    OperationType.Balance_Change: balance_change,

    # --------------------
    # Trends / Time
    # --------------------
    OperationType.Spending_Trends: spending_trends,
    OperationType.Monthly_Summary: monthly_summary,
    OperationType.Compose_Periods: compare_periods,

    # --------------------
    # Transactions
    # --------------------
    OperationType.Recent_Operations: recent_operations,
    OperationType.Largest_Transactions: largest_transaction,

    # --------------------
    # Summary
    # --------------------
    OperationType.Account_Summary: account_summary_handler,
    OperationType.User_Accounts:get_user_accounts_service,

}
