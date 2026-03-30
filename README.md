# Agentic Finance Manager

Agentic Finance Manager is a FastAPI-based personal finance backend with JWT auth, account and transaction management, OTP email verification, and a LangGraph-powered finance chatbot. The repo also includes two client UIs for testing the API: a standalone browser frontend in `frontend/` and a Streamlit API lab.

## Overview

- FastAPI backend with modular route files for auth, users, accounts, transactions, and chatbot access
- PostgreSQL persistence through SQLAlchemy models
- JWT authentication with email verification before protected finance actions
- LangGraph chatbot pipeline for finance summaries, numeric questions, and visualization-oriented responses
- Standalone frontend for register, verify OTP, login, logout, account, transaction, and raw API testing
- Streamlit API lab for interactive endpoint testing and chat flows

## Workflow Diagram

![Agentic Chatbot Flow](./output.png)

## Main Features

- User registration with password hashing
- Email verification using OTP sent through Gmail SMTP
- Login with JWT access tokens at `/login`
- Fetch current authenticated user at `/users/me`
- Resend OTP using email
- Update or delete user flows
- Create up to 3 accounts per user
- Create accounts with an initial income transaction
- Track balances directly on each account
- Create, list, update, fetch, and delete transactions
- Expense safety checks to prevent spending beyond account balance
- Chat endpoint at `/chat/chat`
- Query decomposition and expansion before execution
- Numeric operations such as current balance, total income, total expense, and balance change
- Summary operations for account and transaction explanations
- Visualization-oriented outputs for income vs expense and category-wise spending

## Tech Stack

- Python 3.12+
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT / OAuth2 password flow
- LangChain
- LangGraph
- Groq LLM integration
- Streamlit

## Repo Structure

```text
.
|-- main.py
|-- database.py
|-- models.py
|-- oauth2.py
|-- utils.py
|-- streamlit_app.py
|-- init_db.py
|-- create_test_user.py
|-- output.png
|-- frontend/
|   |-- index.html
|   |-- app.js
|   |-- styles.css
|-- routes/
|   |-- auth_routes.py
|   |-- user.py
|   |-- accounts_routes.py
|   |-- transactions_routes.py
|-- schemas/
|   |-- accounts/
|   |-- chatbot/
|   |-- email/
|   |-- token/
|   |-- transactions/
|   |-- users/
|-- chatbot/
|   |-- graph.py
|   |-- operations.py
|   |-- practice.py
|   |-- state_manager.py
|   |-- prompts/
|   |-- nodes/
|   |-- services/
```

## Chatbot Graph

The chatbot graph defined in [chatbot/graph.py](./chatbot/graph.py) currently follows this flow:

1. `decompose_query`
2. `pick_sub_query`
3. `multi_query_generation`
4. `pick_expanded_query`
5. `intent_classifier`
6. `get_operations`
7. Route to one of:
   `numeric_pipeline`
   `summary_pipeline`
   `visualize_pipeline`
8. `increment_expanded_index`
9. Loop across expanded queries
10. `increment_index`
11. Loop across sub-queries or finish
12. `final_result`

## API Modules

- `routes/auth_routes.py`: login and JWT issuance
- `routes/user.py`: register, verify email, resend OTP, current user, update, delete
- `routes/accounts_routes.py`: create/list/detail/summary/balance/delete account routes
- `routes/transactions_routes.py`: create/list/get/update/delete transactions
- `chatbot/graph.py`: chat router and LangGraph workflow

## Environment Variables

Create a `.env` file in the project root with the values used by the repo:

```env
GMAIL_ID=your_email@gmail.com
PASSWORD=your_gmail_app_password

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

POSTGRES_DB_NAME=your_database_name
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password

GROQ_API_KEY=your_groq_api_key
```

Notes:

- `GMAIL_ID` and `PASSWORD` are used for OTP email sending.
- `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES` are required by JWT auth.
- PostgreSQL is expected at `localhost:5432` in the current database setup.
- `GROQ_API_KEY` is used by chatbot nodes that call the LLM.

## Setup

1. Clone the repo.

```bash
git clone <your-repo-url>
cd Agentic_Graph
```

2. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Make sure PostgreSQL is running locally on port `5432`.

5. Add the `.env` file shown above.

6. Start the API server.

```bash
uvicorn main:app --reload
```

## Running the Frontends

### Standalone Frontend

Open [frontend/index.html](./frontend/index.html) in your browser after the API server is running.

This UI supports:

- register
- verify OTP
- resend OTP
- login/logout
- account creation and selection
- transaction creation and updates
- chatbot requests
- raw API request testing

### Streamlit API Lab

Run:

```bash
streamlit run streamlit_app.py
```

The Streamlit app provides:

- quick login/logout
- user creation and email verification
- account and transaction API testing
- embedded chatbot requests
- API response history

## API Docs

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Current Data Model Notes

- Supported account types: `savings`, `checking`, `credit`
- Supported transaction types: `income`, `expense`
- Supported transaction categories: `food`, `shopping`, `utilities`, `entertainment`, `transportation`, `other`

## Helpful Files

- [main.py](./main.py): FastAPI app wiring and router registration
- [models.py](./models.py): SQLAlchemy models and enums
- [oauth2.py](./oauth2.py): token creation and current-user resolution
- [utils.py](./utils.py): hashing, OTP generation, email sending, and helper utilities
- [frontend/app.js](./frontend/app.js): standalone frontend logic
- [streamlit_app.py](./streamlit_app.py): Streamlit API lab

## Notes

- CORS is currently open to all origins.
- Tables are created on app startup via `Base.metadata.create_all(bind=engine)`.
- The chatbot is mounted under `/chat`.
- The project contains both `requirements.txt` and `pyproject.toml`, but `requirements.txt` is the most direct install path for this repo state.
