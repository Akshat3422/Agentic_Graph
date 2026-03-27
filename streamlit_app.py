import streamlit as st
import requests


# -----------------------------
# Basic configuration
# -----------------------------
st.set_page_config(page_title="Financial Assistant", layout="wide")

st.title("Financial Assistant Frontend")

backend_url = st.sidebar.text_input(
    "Backend URL",
    value="http://localhost:8000",
    help="Base URL of your FastAPI backend",
)


def api_request(method: str, path: str, token: str | None = None, **kwargs):
    url = backend_url.rstrip("/") + path
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        resp = requests.request(method, url, headers=headers, timeout=15, **kwargs)
        if resp.headers.get("content-type", "").startswith("application/json"):
            data = resp.json()
        else:
            data = resp.text
        return resp.status_code, data
    except Exception as e:
        return 0, {"error": str(e)}


def render_response(resp):
    if isinstance(resp, (dict, list)):
        st.json(resp)
    else:
        st.code(str(resp))


# -----------------------------
# Auth / session
# -----------------------------
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

st.sidebar.subheader("Authentication")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

col_login1, col_login2 = st.sidebar.columns(2)
with col_login1:
    if st.button("Login"):
        data = {"username": username, "password": password}
        status, resp = api_request(
            "POST",
            "/login",
            data=data,
        )
        if status == 200 and isinstance(resp, dict) and "access_token" in resp:
            st.session_state["access_token"] = resp["access_token"]
            st.sidebar.success("Logged in successfully")
        else:
            st.sidebar.error(f"Login failed: {resp}")
with col_login2:
    if st.button("Logout"):
        st.session_state["access_token"] = None
        st.sidebar.info("Logged out")

token = st.session_state["access_token"]
st.sidebar.markdown(
    f"**Token status:** {'✅ Set' if token else '❌ Not set'}"
)


# -----------------------------
# Tabs for main APIs
# -----------------------------
tab_users, tab_accounts, tab_transactions, tab_chat = st.tabs(
    ["Users", "Accounts", "Transactions", "Chatbot"]
)


# -----------------------------
# Users tab
# -----------------------------
with tab_users:
    st.header("Users API")

    st.subheader("Create User")
    with st.form("create_user_form"):
        cu_username = st.text_input("New username")
        cu_email = st.text_input("Email")
        cu_password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Create user")
        if submitted:
            payload = {
                "username": cu_username,
                "email": cu_email,
                "password": cu_password,
            }
            status, resp = api_request("POST", "/users/", json=payload)
            st.write("Status:", status)
            render_response(resp)

    st.subheader("Verify Email OTP")
    with st.form("verify_email_form"):
        v_email = st.text_input("Email to verify")
        v_otp = st.text_input("OTP")
        submitted = st.form_submit_button("Verify email")
        if submitted:
            payload = {"email": v_email, "otp": v_otp}
            status, resp = api_request("POST", "/users/verify-email", json=payload)
            st.write("Status:", status)
            render_response(resp)

    st.subheader("Current User (/users/me)")
    if st.button("Get current user", disabled=not token):
        status, resp = api_request("GET", "/users/me", token=token)
        st.write("Status:", status)
        render_response(resp)

    st.subheader("Resend Email OTP")
    if st.button("Resend OTP", disabled=not token):
        status, resp = api_request("POST", "/users/resend-otp", token=token)
        st.write("Status:", status)
        render_response(resp)


# -----------------------------
# Accounts tab
# -----------------------------
with tab_accounts:
    st.header("Accounts API")

    st.subheader("Create Account (with initial transaction)")
    with st.form("create_account_form"):
        acc_name = st.text_input("Account name")
        acc_type = st.selectbox(
            "Account type",
            options=["savings", "current", "credit"],
        )
        init_amount = st.number_input("Initial balance amount", min_value=0.0, step=100.0)
        init_category = st.text_input("Initial category (e.g. salary)")
        init_desc = st.text_input("Initial description", value="Initial deposit")
        submitted = st.form_submit_button("Create account", disabled=not token)
        if submitted:
            account_details = {
                "account_name": acc_name,
                "account_type": acc_type,
            }
            initial_transaction = {
                "transaction_type": "income",
                "amount": init_amount,
                "description": init_desc,
                "category": init_category,
                "timestamp": None,
            }
            status, resp = api_request(
                "POST",
                "/accounts/",
                token=token,
                json={
                    "account_details": account_details,
                    "initial_transaction": initial_transaction,
                },
            )
            st.write("Status:", status)
            render_response(resp)

    st.subheader("List My Accounts")
    if st.button("Get my accounts", disabled=not token):
        status, resp = api_request("GET", "/accounts/", token=token)
        st.write("Status:", status)
        render_response(resp)

    st.subheader("Get Single Account")
    acc_id_single = st.number_input(
        "Account ID (details / summary / balance / delete)",
        min_value=0,
        step=1,
    )
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        if st.button("Details", disabled=not token):
            status, resp = api_request(
                "GET", f"/accounts/{int(acc_id_single)}", token=token
            )
            st.write("Status:", status)
            render_response(resp)
    with col_a2:
        if st.button("Summary", disabled=not token):
            status, resp = api_request(
                "GET", f"/accounts/summary/{int(acc_id_single)}", token=token
            )
            st.write("Status:", status)
            render_response(resp)
    with col_a3:
        if st.button("Balance", disabled=not token):
            status, resp = api_request(
                "GET",
                f"/accounts/summmary/{int(acc_id_single)}/balance",
                token=token,
            )
            st.write("Status:", status)
            render_response(resp)
    with col_a4:
        if st.button("Delete account", disabled=not token):
            status, resp = api_request(
                "DELETE", f"/accounts/delete/{int(acc_id_single)}", token=token
            )
            st.write("Status:", status)
            render_response(resp)


# -----------------------------
# Transactions tab
# -----------------------------
with tab_transactions:
    st.header("Transactions API")

    st.subheader("Create Transaction")
    with st.form("create_tx_form"):
        tx_account_id = st.number_input(
            "Account ID", min_value=0, step=1, key="tx_account_id_create"
        )
        tx_type = st.selectbox("Type", options=["income", "expense"])
        tx_amount = st.number_input("Amount", min_value=0.0, step=100.0)
        tx_category = st.text_input("Category")
        tx_desc = st.text_input("Description")
        submitted = st.form_submit_button("Create transaction", disabled=not token)
        if submitted:
            tx_body = {
                "transaction_type": tx_type,
                "amount": tx_amount,
                "description": tx_desc,
                "category": tx_category,
                "timestamp": None,
            }
            status, resp = api_request(
                "POST",
                "/transactions/",
                token=token,
                params={"account_id": int(tx_account_id)},
                json=tx_body,
            )
            st.write("Status:", status)
            render_response(resp)

    st.subheader("Get / Update / Delete Transaction")
    tx_id = st.number_input("Transaction ID", min_value=0, step=1, key="tx_id")
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        if st.button("Get transaction", disabled=not token):
            status, resp = api_request(
                "GET", f"/transactions/{int(tx_id)}", token=token
            )
            st.write("Status:", status)
            render_response(resp)
    with col_t2:
        if st.button("Delete transaction", disabled=not token):
            status, resp = api_request(
                "DELETE", f"/transactions/{int(tx_id)}", token=token
            )
            st.write("Status:", status)
            render_response(resp)
    with col_t3:
        with st.expander("Update transaction body"):
            up_amount = st.number_input(
                "New amount (optional)", min_value=0.0, step=100.0, key="up_amount"
            )
            up_type = st.selectbox(
                "New type (optional)", options=["", "income", "expense"], key="up_type"
            )
            up_desc = st.text_input("New description (optional)", key="up_desc")
            up_category = st.text_input("New category (optional)", key="up_cat")
        if st.button("Update transaction", disabled=not token):
            body = {
                "amount": up_amount or None,
                "transaction_type": up_type or None,
                "description": up_desc or None,
                "category": up_category or None,
                "timestamp": None,
            }
            status, resp = api_request(
                "PUT",
                f"/transactions/{int(tx_id)}",
                token=token,
                json=body,
            )
            st.write("Status:", status)
            render_response(resp)

    st.subheader("List Account Transactions")
    tx_account_list_id = st.number_input(
        "Account ID (list txns)", min_value=0, step=1, key="tx_account_list"
    )
    if st.button("Get account transactions", disabled=not token):
        status, resp = api_request(
            "GET", f"/transactions/account/{int(tx_account_list_id)}", token=token
        )
        st.write("Status:", status)
        render_response(resp)


# -----------------------------
# Chatbot tab
# -----------------------------
with tab_chat:
    st.header("Chatbot API")
    st.write("This calls your `/chat/chat` endpoint.")

    chat_input = st.text_area("Your question")
    if st.button("Ask", disabled=not token):
        status, resp = api_request(
            "POST",
            "/chat/chat",
            token=token,
            params={"user_input": chat_input},
        )
        st.write("Status:", status)
        render_response(resp)


