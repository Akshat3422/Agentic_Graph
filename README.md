# 🤖💰 Agentic Finance Manager

An **Agentic AI-powered Finance Management System** built with **FastAPI** and a **graph-based chatbot architecture**.  
The system combines traditional backend APIs (users, accounts, transactions) with an **agentic reasoning layer** that intelligently decomposes queries, classifies intent, and routes them through specialized pipelines.

---

## 🚀 Project Overview

This project consists of **two tightly integrated layers**:

### 1️⃣ Finance Manager Backend
- User authentication & email verification
- Account management
- Transaction handling
- Secure JWT-based APIs

### 2️⃣ Agentic Chatbot Layer
- Graph-based control flow
- Query decomposition
- Intent classification
- Numeric & summarization pipelines
- Iterative reasoning loop

👉 **Both layers belong to the same project and work together.**

---

## 🧠 Agentic Chatbot Architecture

The chatbot follows a **state-driven agent graph**, where each node performs a single responsibility and the flow dynamically adapts based on intent.

### 🔁 Workflow Diagram

![Agentic Chatbot Flow](./output.png)

### 🔄 Flow Explanation

1. **start** – Entry point  
2. **decompose_query** – Breaks complex queries into sub-queries  
3. **pick_sub_query** – Selects next sub-query to process  
4. **intent_classifier** – Detects intent (numeric / summary / continue)  
5. **get_operations** – Chooses execution path  
6. **numeric_pipeline** – Handles calculations & numeric reasoning  
7. **summary_pipeline** – Handles summarization & explanations  
8. **final_result** – Aggregates response  
9. **increment_index** – Moves to next sub-query  
10. **continue loop** – Repeats until completion  
11. **_end** – Terminates execution  

---

## ✨ Features

### 👤 User Management
- User registration
- Email verification via OTP
- Login with JWT
- Get current user
- Update user profile
- Resend OTP
- Delete user account

### 🏦 Account Management
- Create accounts (checking, savings, etc.)
- Fetch all user accounts
- Get account details
- Account summary
- Account balance
- Delete account

### 💸 Transactions
- Create income & expense transactions
- Categorized transactions
- View transactions per account

### 🤖 Agentic Intelligence
- Multi-step query reasoning
- Intent-aware execution
- Modular pipelines
- Stateful graph execution

---

## 🛠 Tech Stack

- **Language:** Python  
- **Backend Framework:** FastAPI  
- **ORM:** SQLAlchemy  
- **Authentication:** JWT (Bearer Token)  
- **Agent Framework:** LangGraph / Custom StateGraph  
- **LLMs:** Pluggable (Groq / OpenAI / others)  
- **API Testing:** Postman  
- **Version Control:** Git & GitHub  

---

## 📂 Project Structure (High Level)

```text
.
├── app/
│   ├── auth/
│   ├── users/
│   ├── accounts/
│   ├── transactions/
│   ├── agent/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── nodes/
│   │   │   ├── decompose_query.py
│   │   │   ├── pick_sub_query.py
│   │   │   ├── intent_classifier.py
│   │   │   ├── numeric_pipeline.py
│   │   │   ├── summary_pipeline.py
│   │   │   └── final_result.py
│   └── main.py
├── diagrams/
│   └── output.png
├── postman_collection.json
├── .env.example
├── requirements.txt
└── README.md
---


## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/Agentic_Graph.git
cd Agentic_Graph


2️⃣ Create & Activate Virtual Environment
Windows
python -m venv .venv
.venv\Scripts\activate

macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Environment Variables

Create a .env file (do NOT commit this file):

DATABASE_URL=postgresql://user:password@localhost:5432/finance_db
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
LLM_API_KEY=your_llm_api_key


Use .env.example as reference.

5️⃣ Run the Application
uvicorn app.main:app --reload


Server will start at:

http://127.0.0.1:8000

📑 API Documentation

FastAPI automatically generates docs:

Swagger UI
http://127.0.0.1:8000/docs

ReDoc
http://127.0.0.1:8000/redoc

🧪 API Testing (Postman)

Import the provided Postman collection

Set environment variable:

localhost = http://127.0.0.1:8000


Login endpoint stores access_token

Protected endpoints require Bearer Token

🔐 Security Notes

.env files are ignored using .gitignore

Secrets are never committed

Compatible with GitHub Push Protection

Rotate keys immediately if exposed

📈 Future Enhancements

Budget forecasting with AI

Expense analytics dashboard

Tool-calling agents

Persistent memory (Vector DB)

Frontend chat UI

👨‍💻 Author

Akshat Gupta
Backend & AI Engineer
FastAPI • Agentic AI • LangGraph

