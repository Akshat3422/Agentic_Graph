const BASE_URL = "http://127.0.0.1:8000";

function show(data) {
  document.getElementById("output").textContent =
    JSON.stringify(data, null, 2);
}

function token() {
  return localStorage.getItem("access_token");
}

/* 1️⃣ CREATE USER */
async function createUser() {
  const res = await fetch(`${BASE_URL}/users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: email.value,
      username: username.value,
      password: newPassword.value,
      is_active: true
    })
  });
  show(await res.json());
}

/* 2️⃣ VERIFY EMAIL */
async function verifyEmail() {
  const res = await fetch(`${BASE_URL}/users/verify-email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: email.value,
      otp: otp.value
    })
  });
  show(await res.json());
}

/* 3️⃣ LOGIN */
async function login() {
  const res = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams({
      username: username.value,
      password: newPassword.value
    })
  });

  const data = await res.json();
  localStorage.setItem("access_token", data.access_token);
  show(data);
}

/* 4️⃣ CREATE ACCOUNT */
async function createAccount() {
  const res = await fetch(`${BASE_URL}/accounts/`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token()}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      account_details: {
        account_name: "AKSHAT ACCOUNT",
        account_type: "checking",
        balance: 0
      },
      initial_transaction: {
        transaction_type: "income",
        amount: 10000,
        description: "initial",
        category: "other"
      }
    })
  });
  show(await res.json());
}

/* 5️⃣ CREATE TRANSACTION */
async function createTransaction() {
  const res = await fetch(
    `${BASE_URL}/transactions/?account_id=${accountId.value}`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token()}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        transaction_type: "expense",
        amount: 2000,
        description: "party",
        category: "food"
      })
    }
  );
  show(await res.json());
}
