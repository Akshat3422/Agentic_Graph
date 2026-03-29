import streamlit as st
import requests
import json
from datetime import datetime


st.set_page_config(page_title="Financial Assistant API Lab", layout="wide")


def init_state():
    defaults = {
        "access_token": None,
        "user_profile": None,
        "user_id": None,
        "account_id": None,
        "accounts_cache": [],
        "last_response": None,
        "chat_history_account": [],
        "chat_history_tx": [],
        "api_history": [],
        "tx_cache": [],
        "theme": "Dark",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def api_request(base_url, method, path, token=None, **kwargs):
    url = base_url.rstrip("/") + path
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.request(method, url, headers=headers, timeout=20, **kwargs)
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
        else:
            data = response.text
        payload = {"status": response.status_code, "path": path, "response": data}
        st.session_state["last_response"] = payload
        st.session_state["api_history"].append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "method": method,
                "path": path,
                "status": response.status_code,
                "ok": response.status_code < 400,
            }
        )
        return response.status_code, data
    except Exception as exc:
        err = {"error": str(exc)}
        st.session_state["last_response"] = {"status": 0, "path": path, "response": err}
        st.session_state["api_history"].append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "method": method,
                "path": path,
                "status": 0,
                "ok": False,
            }
        )
        return 0, err


def render_api_result(status_code, data):
    if status_code and status_code < 400:
        st.success(f"Status: {status_code}")
    else:
        st.error(f"Status: {status_code}")
    if isinstance(data, (dict, list)):
        st.json(data)
    else:
        st.code(str(data))


def fetch_current_user(base_url):
    token = st.session_state["access_token"]
    if not token:
        return
    status, data = api_request(base_url, "GET", "/users/me", token=token)
    if status == 200 and isinstance(data, dict):
        st.session_state["user_profile"] = data
        st.session_state["user_id"] = data.get("id")


def fetch_accounts(base_url):
    token = st.session_state["access_token"]
    if not token:
        return []
    status, data = api_request(base_url, "GET", "/accounts/", token=token)
    if status == 200 and isinstance(data, list):
        st.session_state["accounts_cache"] = data
        return data
    return []


def apply_theme(theme_name):
    if theme_name == "Light":
        style = """
        <style>
        .main-title {font-size: 2.1rem; font-weight: 700; margin-bottom: 0.3rem; color: #111827;}
        .subtitle {color: #1d4ed8; margin-bottom: 1rem;}
        .card {padding: 0.8rem 1rem; border-radius: 12px; border: 1px solid #c7d2fe; background: #eff6ff;}
        </style>
        """
    else:
        style = """
        <style>
        .main-title {font-size: 2.1rem; font-weight: 700; margin-bottom: 0.3rem;}
        .subtitle {color: #91a7ff; margin-bottom: 1rem;}
        .card {padding: 0.8rem 1rem; border-radius: 12px; border: 1px solid #2f2f44; background: #111827;}
        </style>
        """
    st.markdown(style, unsafe_allow_html=True)


def send_chat(base_url, prompt_text, section_name):
    token = st.session_state["access_token"]
    if not token:
        st.warning("Login first to use chatbot.")
        return
    status, data = api_request(
        base_url,
        "POST",
        "/chat/chat",
        token=token,
        params={"user_input": prompt_text},
    )
    history_key = "chat_history_account" if section_name == "account" else "chat_history_tx"
    st.session_state[history_key].append(
        {
            "question": prompt_text,
            "answer": data,
            "status": status,
        }
    )
    render_api_result(status, data)


init_state()
st.session_state["theme"] = st.sidebar.radio("Theme", ["Dark", "Light"], index=0 if st.session_state["theme"] == "Dark" else 1)
apply_theme(st.session_state["theme"])
st.markdown('<div class="main-title">Financial Assistant API Lab</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Interactive frontend for login, account, transactions, and chatbot API testing.</div>',
    unsafe_allow_html=True,
)

backend_url = st.sidebar.text_input("Backend URL", value="http://localhost:8000")
st.sidebar.markdown("### Session")
st.sidebar.write(f"Token: {'Yes' if st.session_state['access_token'] else 'No'}")
st.sidebar.write(f"user_id: {st.session_state['user_id']}")
st.sidebar.write(f"account_id: {st.session_state['account_id']}")

st.sidebar.markdown("### Login")
login_user = st.sidebar.text_input("Username")
login_pass = st.sidebar.text_input("Password", type="password")
col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    if st.button("Login", use_container_width=True):
        status, data = api_request(
            backend_url, "POST", "/login", data={"username": login_user, "password": login_pass}
        )
        if status == 200 and isinstance(data, dict) and "access_token" in data:
            st.session_state["access_token"] = data["access_token"]
            fetch_current_user(backend_url)
            st.sidebar.success("Login successful and user_id fetched.")
        else:
            st.sidebar.error("Login failed.")
with col_s2:
    if st.button("Logout", use_container_width=True):
        st.session_state["access_token"] = None
        st.session_state["user_profile"] = None
        st.session_state["user_id"] = None
        st.session_state["account_id"] = None
        st.sidebar.info("Logged out.")

c1, c2, c3 = st.columns(3)
c1.metric("Logged in user_id", st.session_state["user_id"] or "N/A")
c2.metric("Selected account_id", st.session_state["account_id"] or "N/A")
c3.metric("Cached accounts", len(st.session_state["accounts_cache"]))

tab_users, tab_accounts, tab_transactions, tab_api = st.tabs(
    ["Users", "Accounts + Chat", "Transactions + Chat", "API Console"]
)

with tab_users:
    st.subheader("Create and verify users")
    with st.form("create_user"):
        n_user = st.text_input("Username")
        n_email = st.text_input("Email")
        n_pass = st.text_input("Password", type="password")
        if st.form_submit_button("Create User"):
            status, data = api_request(
                backend_url,
                "POST",
                "/users/",
                json={"username": n_user, "email": n_email, "password": n_pass},
            )
            render_api_result(status, data)

    with st.form("verify_user"):
        v_email = st.text_input("Verify email")
        otp = st.text_input("OTP")
        if st.form_submit_button("Verify Email"):
            status, data = api_request(
                backend_url, "POST", "/users/verify-email", json={"email": v_email, "otp": otp}
            )
            render_api_result(status, data)

    a1, a2 = st.columns(2)
    with a1:
        if st.button("Get /users/me", disabled=not st.session_state["access_token"]):
            fetch_current_user(backend_url)
            render_api_result(200, st.session_state["user_profile"])
    with a2:
        if st.button("Resend OTP", disabled=not st.session_state["access_token"]):
            status, data = api_request(
                backend_url, "POST", "/users/resend-otp", token=st.session_state["access_token"]
            )
            render_api_result(status, data)

with tab_accounts:
    st.subheader("Accounts testing with auto-selected account_id")
    if st.button("Refresh My Accounts", disabled=not st.session_state["access_token"]):
        accs = fetch_accounts(backend_url)
        if accs:
            st.success("Accounts fetched.")
    accounts = st.session_state["accounts_cache"]
    if accounts:
        total_balance = sum(float(acc.get("balance", 0) or 0) for acc in accounts)
        by_type = {}
        for acc in accounts:
            acc_type = str(acc.get("account_type", "unknown"))
            by_type[acc_type] = by_type.get(acc_type, 0) + float(acc.get("balance", 0) or 0)
        k1, k2 = st.columns(2)
        k1.metric("Total account balance", f"{total_balance:.2f}")
        k2.metric("Total accounts", len(accounts))
        st.caption("Balance by account type")
        st.bar_chart(by_type)
    options = []
    for acc in accounts:
        options.append((acc.get("id"), f"{acc.get('id')} - {acc.get('account_name')} ({acc.get('account_type')})"))
    if options:
        selected_label = st.selectbox("Choose account", [label for _, label in options])
        chosen_id = [aid for aid, lbl in options if lbl == selected_label][0]
        st.session_state["account_id"] = int(chosen_id)
    else:
        st.info("No accounts loaded. Click 'Refresh My Accounts'.")

    with st.form("create_account"):
        st.markdown("#### Create account")
        acc_name = st.text_input("Account name")
        acc_type = st.selectbox("Account type", ["savings", "current", "credit"])
        init_amount = st.number_input("Initial income amount", min_value=0.0, step=100.0)
        init_category = st.text_input("Initial category", value="salary")
        init_desc = st.text_input("Initial description", value="Initial deposit")
        if st.form_submit_button("Create Account", disabled=not st.session_state["access_token"]):
            status, data = api_request(
                backend_url,
                "POST",
                "/accounts/",
                token=st.session_state["access_token"],
                json={
                    "account_details": {"account_name": acc_name, "account_type": acc_type},
                    "initial_transaction": {
                        "transaction_type": "income",
                        "amount": init_amount,
                        "description": init_desc,
                        "category": init_category,
                        "timestamp": None,
                    },
                },
            )
            render_api_result(status, data)
            fetch_accounts(backend_url)

    current_account_id = st.session_state["account_id"]
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        if st.button("Details", disabled=not (st.session_state["access_token"] and current_account_id)):
            status, data = api_request(
                backend_url,
                "GET",
                f"/accounts/{int(current_account_id)}",
                token=st.session_state["access_token"],
            )
            render_api_result(status, data)
    with d2:
        if st.button("Summary", disabled=not (st.session_state["access_token"] and current_account_id)):
            status, data = api_request(
                backend_url,
                "GET",
                f"/accounts/summary/{int(current_account_id)}",
                token=st.session_state["access_token"],
            )
            render_api_result(status, data)
    with d3:
        if st.button("Balance", disabled=not (st.session_state["access_token"] and current_account_id)):
            status, data = api_request(
                backend_url,
                "GET",
                f"/accounts/summmary/{int(current_account_id)}/balance",
                token=st.session_state["access_token"],
            )
            render_api_result(status, data)
    with d4:
        if st.button("Delete", disabled=not (st.session_state["access_token"] and current_account_id)):
            status, data = api_request(
                backend_url,
                "DELETE",
                f"/accounts/delete/{int(current_account_id)}",
                token=st.session_state["access_token"],
            )
            render_api_result(status, data)
            st.session_state["account_id"] = None
            fetch_accounts(backend_url)

    st.markdown("---")
    st.markdown("#### Chatbot (Account section)")
    account_prompt = st.text_area("Ask account-related question", key="chat_acc_input")
    if st.button("Ask Chatbot (Account)", disabled=not st.session_state["access_token"]):
        send_chat(backend_url, account_prompt, "account")
    for item in reversed(st.session_state["chat_history_account"][-4:]):
        with st.expander(f"Q: {item['question'][:80]}"):
            st.write(f"Status: {item['status']}")
            if isinstance(item["answer"], (dict, list)):
                st.json(item["answer"])
            else:
                st.code(str(item["answer"]))

with tab_transactions:
    st.subheader("Transactions testing using selected account_id")
    with st.form("create_tx"):
        st.markdown("#### Create transaction")
        tx_type = st.selectbox("Type", ["income", "expense"])
        tx_amount = st.number_input("Amount", min_value=0.0, step=100.0)
        tx_category = st.text_input("Category", value="salary")
        tx_desc = st.text_input("Description", value="transaction entry")
        tx_account_id = st.number_input(
            "Account ID (auto-filled from selected account)",
            min_value=0,
            step=1,
            value=int(st.session_state["account_id"] or 0),
        )
        if st.form_submit_button("Create Transaction", disabled=not st.session_state["access_token"]):
            st.session_state["account_id"] = int(tx_account_id)
            status, data = api_request(
                backend_url,
                "POST",
                "/transactions/",
                token=st.session_state["access_token"],
                params={"account_id": int(tx_account_id)},
                json={
                    "transaction_type": tx_type,
                    "amount": tx_amount,
                    "description": tx_desc,
                    "category": tx_category,
                    "timestamp": None,
                },
            )
            render_api_result(status, data)
            if st.session_state["account_id"]:
                tx_status, tx_data = api_request(
                    backend_url,
                    "GET",
                    f"/transactions/account/{int(st.session_state['account_id'])}",
                    token=st.session_state["access_token"],
                )
                if tx_status == 200 and isinstance(tx_data, list):
                    st.session_state["tx_cache"] = tx_data

    e1, e2 = st.columns(2)
    with e1:
        if st.button("List Transactions of selected account", disabled=not (st.session_state["access_token"] and st.session_state["account_id"])):
            status, data = api_request(
                backend_url,
                "GET",
                f"/transactions/account/{int(st.session_state['account_id'])}",
                token=st.session_state["access_token"],
            )
            render_api_result(status, data)
            if status == 200 and isinstance(data, list):
                st.session_state["tx_cache"] = data
    with e2:
        tx_id = st.number_input("Transaction ID", min_value=0, step=1, key="tx_action_id")
        if st.button("Get Transaction", disabled=not st.session_state["access_token"]):
            status, data = api_request(
                backend_url, "GET", f"/transactions/{int(tx_id)}", token=st.session_state["access_token"]
            )
            render_api_result(status, data)

    with st.expander("Update / Delete Transaction"):
        tx_id_up = st.number_input("Transaction ID to update/delete", min_value=0, step=1, key="tx_up_id")
        up_amount = st.number_input("Updated amount", min_value=0.0, step=100.0)
        up_type = st.selectbox("Updated type", ["", "income", "expense"])
        up_desc = st.text_input("Updated description")
        up_cat = st.text_input("Updated category")
        f1, f2 = st.columns(2)
        with f1:
            if st.button("Update Transaction", disabled=not st.session_state["access_token"]):
                status, data = api_request(
                    backend_url,
                    "PUT",
                    f"/transactions/{int(tx_id_up)}",
                    token=st.session_state["access_token"],
                    json={
                        "amount": up_amount or None,
                        "transaction_type": up_type or None,
                        "description": up_desc or None,
                        "category": up_cat or None,
                        "timestamp": None,
                    },
                )
                render_api_result(status, data)
        with f2:
            if st.button("Delete Transaction", disabled=not st.session_state["access_token"]):
                status, data = api_request(
                    backend_url,
                    "DELETE",
                    f"/transactions/{int(tx_id_up)}",
                    token=st.session_state["access_token"],
                )
                render_api_result(status, data)

    tx_cache = st.session_state["tx_cache"]
    if tx_cache:
        income_total = sum(float(t.get("amount", 0) or 0) for t in tx_cache if t.get("transaction_type") == "income")
        expense_total = sum(float(t.get("amount", 0) or 0) for t in tx_cache if t.get("transaction_type") == "expense")
        t1, t2, t3 = st.columns(3)
        t1.metric("Transactions loaded", len(tx_cache))
        t2.metric("Total income", f"{income_total:.2f}")
        t3.metric("Total expense", f"{expense_total:.2f}")
        st.caption("Transaction totals")
        st.bar_chart({"income": income_total, "expense": expense_total})

    st.markdown("---")
    st.markdown("#### Chatbot (Transaction section)")
    tx_prompt = st.text_area("Ask transaction-related question", key="chat_tx_input")
    if st.button("Ask Chatbot (Transactions)", disabled=not st.session_state["access_token"]):
        send_chat(backend_url, tx_prompt, "tx")
    for item in reversed(st.session_state["chat_history_tx"][-4:]):
        with st.expander(f"Q: {item['question'][:80]}"):
            st.write(f"Status: {item['status']}")
            if isinstance(item["answer"], (dict, list)):
                st.json(item["answer"])
            else:
                st.code(str(item["answer"]))

with tab_api:
    st.subheader("Generic API Console (for quick endpoint testing)")
    method = st.selectbox("Method", ["GET", "POST", "PUT", "DELETE"])
    path = st.text_input("Path", value="/users/me")
    raw_params = st.text_input("Query params (key=value&x=y)", value="")
    raw_json = st.text_area("JSON body", value='{"sample": "value"}')
    if st.button("Send Request"):
        params = {}
        if raw_params.strip():
            for pair in raw_params.split("&"):
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    params[key] = value
        request_kwargs = {"params": params} if params else {}
        if method in ("POST", "PUT") and raw_json.strip():
            try:
                request_kwargs["json"] = __import__("json").loads(raw_json)
            except Exception:
                st.warning("Invalid JSON body. Sending without JSON.")
        status, data = api_request(
            backend_url, method, path, token=st.session_state["access_token"], **request_kwargs
        )
        render_api_result(status, data)

    if st.session_state["last_response"]:
        st.markdown("### Last API Response")
        st.json(st.session_state["last_response"])

    st.markdown("### API Request History")
    if st.session_state["api_history"]:
        st.dataframe(st.session_state["api_history"], use_container_width=True)
        st.download_button(
            label="Download API Logs (JSON)",
            data=json.dumps(st.session_state["api_history"], indent=2),
            file_name=f"api_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )
    else:
        st.info("No API calls made yet.")


