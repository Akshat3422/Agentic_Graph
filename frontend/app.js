
const STORAGE_KEY = "financial-assistant-spa-state";

const state = {
  baseUrl: "http://localhost:8000",
  token: null,
  user: null,
  userId: null,
  accounts: [],
  selectedAccountId: null,
  transactions: [],
  chatHistory: {
    accounts: [],
    transactions: []
  },
  apiHistory: [],
  lastResponse: null,
  activeTab: "dashboard"
};

const el = {};

function cacheElements() {
  const ids = [
    "authShell", "appShell", "authStatus", "backendUrlInput", "activeBackendUrl", "statusText", "pageTitle",
    "sidebar", "sidebarToggle", "sidebarUserName", "sidebarUserEmail", "sidebarUserId", "sidebarAccountId", "sidebarAvatar",
    "metricUser", "metricUserSub", "metricUserId", "metricAccountId", "metricAccountSub", "metricTxCount",
    "dashboardAccountCount", "dashboardBalance", "dashboardIncome", "dashboardExpense", "dashboardTransactions",
    "accountsGrid", "accountActionSelectedId", "accountActionOutput", "accountFormCard",
    "transactionFormCard", "transactionAccountSelect", "transactionCurrentAccountId", "transactionsList",
    "transactionActionOutput", "filterTypeInput", "filterCategoryInput", "txIncomeTotal", "txExpenseTotal",
    "accountsChatLog", "accountsChatInput", "transactionsChatLog", "transactionsChatInput",
    "apiConsoleOutput", "apiHistory", "apiMethodInput", "apiPathInput", "apiParamsInput", "apiBodyInput",
    "toast", "loadingOverlay", "loadingText", "accountsChart", "flowChart", "categoryChart", "trendChart"
  ];

  ids.forEach((id) => {
    el[id] = document.getElementById(id);
  });
}

function hydrateState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const saved = JSON.parse(raw);
    state.baseUrl = saved.baseUrl || state.baseUrl;
    state.token = saved.token || null;
    state.selectedAccountId = saved.selectedAccountId || null;
    state.chatHistory = saved.chatHistory || state.chatHistory;
    state.apiHistory = saved.apiHistory || [];
    state.activeTab = saved.activeTab || state.activeTab;
  } catch (error) {
    console.warn("Unable to restore saved state", error);
  }
}

function persistState() {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      baseUrl: state.baseUrl,
      token: state.token,
      selectedAccountId: state.selectedAccountId,
      chatHistory: state.chatHistory,
      apiHistory: state.apiHistory.slice(0, 25),
      activeTab: state.activeTab
    })
  );
}

function setStatus(message) {
  el.statusText.textContent = message;
}

function setLoading(isLoading, message = "Loading...") {
  el.loadingOverlay.classList.toggle("hidden", !isLoading);
  el.loadingText.textContent = message;
}

function showToast(message, type = "info") {
  el.toast.textContent = message;
  el.toast.className = `toast show ${type}`;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    el.toast.className = "toast";
  }, 2800);
}

function setAuthBanner(message, type = "info") {
  el.authStatus.textContent = message;
  el.authStatus.className = `inline-banner ${type}`;
}

function formatCurrency(value) {
  const num = Number(value || 0);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2
  }).format(Number.isFinite(num) ? num : 0);
}

function formatDate(value) {
  if (!value) return "No timestamp";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

function formatJson(value) {
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch (_) {
    return String(value);
  }
}

function clearCanvas(canvas) {
  if (!canvas) return null;
  const rect = canvas.getBoundingClientRect();
  const width = Math.max(Math.floor(rect.width || canvas.width || 300), 300);
  const height = Math.max(Math.floor(canvas.height || rect.height || 220), 220);
  canvas.width = width;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, width, height);
  return { ctx, width, height };
}

function drawEmptyChart(canvas, title) {
  const surface = clearCanvas(canvas);
  if (!surface) return;
  const { ctx, width, height } = surface;
  ctx.fillStyle = "rgba(111, 90, 77, 0.9)";
  ctx.font = "600 18px Space Grotesk";
  ctx.textAlign = "center";
  ctx.fillText(title, width / 2, height / 2 - 8);
  ctx.font = "14px Space Grotesk";
  ctx.fillStyle = "rgba(111, 90, 77, 0.78)";
  ctx.fillText("Load some data to render this chart.", width / 2, height / 2 + 20);
}

function drawBarChart(canvas, items, options = {}) {
  if (!items.length) {
    drawEmptyChart(canvas, options.emptyTitle || "No chart data");
    return;
  }
  const surface = clearCanvas(canvas);
  if (!surface) return;
  const { ctx, width, height } = surface;
  const padding = { top: 24, right: 18, bottom: 44, left: 28 };
  const chartHeight = height - padding.top - padding.bottom;
  const chartWidth = width - padding.left - padding.right;
  const maxValue = Math.max(...items.map((item) => item.value), 1);
  const gap = 14;
  const barWidth = Math.max((chartWidth - gap * (items.length - 1)) / items.length, 18);

  ctx.strokeStyle = "rgba(78, 53, 36, 0.15)";
  ctx.lineWidth = 1;
  for (let i = 0; i < 4; i += 1) {
    const y = padding.top + (chartHeight / 3) * i;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(width - padding.right, y);
    ctx.stroke();
  }

  items.forEach((item, index) => {
    const x = padding.left + index * (barWidth + gap);
    const barHeight = (item.value / maxValue) * (chartHeight - 10);
    const y = padding.top + chartHeight - barHeight;
    const gradient = ctx.createLinearGradient(0, y, 0, padding.top + chartHeight);
    gradient.addColorStop(0, item.color);
    gradient.addColorStop(1, "rgba(255,255,255,0.65)");
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.roundRect(x, y, barWidth, barHeight, 14);
    ctx.fill();

    ctx.fillStyle = "rgba(32, 23, 19, 0.92)";
    ctx.font = "600 12px Space Grotesk";
    ctx.textAlign = "center";
    ctx.fillText(item.label, x + barWidth / 2, height - 14);
    ctx.fillStyle = "rgba(111, 90, 77, 0.9)";
    ctx.fillText(shortCurrency(item.value), x + barWidth / 2, y - 8);
  });
}

function drawLineChart(canvas, values, options = {}) {
  if (!values.length) {
    drawEmptyChart(canvas, options.emptyTitle || "No trend data");
    return;
  }
  const surface = clearCanvas(canvas);
  if (!surface) return;
  const { ctx, width, height } = surface;
  const padding = { top: 28, right: 18, bottom: 38, left: 20 };
  const chartHeight = height - padding.top - padding.bottom;
  const chartWidth = width - padding.left - padding.right;
  const maxValue = Math.max(...values.map((item) => item.value), 1);
  const minValue = Math.min(...values.map((item) => item.value), 0);
  const range = Math.max(maxValue - minValue, 1);

  ctx.strokeStyle = "rgba(78, 53, 36, 0.15)";
  for (let i = 0; i < 4; i += 1) {
    const y = padding.top + (chartHeight / 3) * i;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(width - padding.right, y);
    ctx.stroke();
  }

  const points = values.map((item, index) => {
    const x = padding.left + (chartWidth / Math.max(values.length - 1, 1)) * index;
    const y = padding.top + chartHeight - ((item.value - minValue) / range) * chartHeight;
    return { x, y, label: item.label, value: item.value };
  });

  ctx.beginPath();
  points.forEach((point, index) => {
    if (index === 0) ctx.moveTo(point.x, point.y);
    else ctx.lineTo(point.x, point.y);
  });
  ctx.strokeStyle = options.lineColor || "#0b6e69";
  ctx.lineWidth = 3;
  ctx.stroke();

  const area = ctx.createLinearGradient(0, padding.top, 0, height - padding.bottom);
  area.addColorStop(0, "rgba(11, 110, 105, 0.22)");
  area.addColorStop(1, "rgba(11, 110, 105, 0.02)");
  ctx.beginPath();
  points.forEach((point, index) => {
    if (index === 0) ctx.moveTo(point.x, point.y);
    else ctx.lineTo(point.x, point.y);
  });
  ctx.lineTo(points[points.length - 1].x, height - padding.bottom);
  ctx.lineTo(points[0].x, height - padding.bottom);
  ctx.closePath();
  ctx.fillStyle = area;
  ctx.fill();

  points.forEach((point) => {
    ctx.fillStyle = options.dotColor || "#b85c38";
    ctx.beginPath();
    ctx.arc(point.x, point.y, 4.5, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "rgba(111, 90, 77, 0.9)";
    ctx.font = "600 11px Space Grotesk";
    ctx.textAlign = "center";
    ctx.fillText(point.label, point.x, height - 12);
  });
}

function shortCurrency(value) {
  const num = Number(value || 0);
  if (Math.abs(num) >= 1000) {
    return `$${(num / 1000).toFixed(1)}k`;
  }
  return `$${num.toFixed(0)}`;
}

function renderCharts() {
  const byType = {};
  state.accounts.forEach((account) => {
    const key = account.account_type || "unknown";
    byType[key] = (byType[key] || 0) + Number(account.balance || 0);
  });
  drawBarChart(
    el.accountsChart,
    Object.entries(byType).map(([label, value], index) => ({
      label,
      value,
      color: ["#b85c38", "#0b6e69", "#934a68", "#567c2d"][index % 4]
    })),
    { emptyTitle: "No account balances yet" }
  );

  const income = state.transactions
    .filter((tx) => tx.transaction_type === "income")
    .reduce((sum, tx) => sum + Number(tx.amount || 0), 0);
  const expense = state.transactions
    .filter((tx) => tx.transaction_type === "expense")
    .reduce((sum, tx) => sum + Number(tx.amount || 0), 0);
  drawBarChart(
    el.flowChart,
    [
      { label: "income", value: income, color: "#0b6e69" },
      { label: "expense", value: expense, color: "#b85c38" }
    ].filter((item) => item.value > 0),
    { emptyTitle: "No income / expense data yet" }
  );

  const byCategory = {};
  state.transactions
    .filter((tx) => tx.transaction_type === "expense")
    .forEach((tx) => {
      const key = tx.category || "other";
      byCategory[key] = (byCategory[key] || 0) + Number(tx.amount || 0);
    });
  drawBarChart(
    el.categoryChart,
    Object.entries(byCategory).map(([label, value], index) => ({
      label,
      value,
      color: ["#934a68", "#d47b45", "#0b6e69", "#567c2d", "#6f5a4d"][index % 5]
    })),
    { emptyTitle: "No spending categories yet" }
  );

  const recentTrend = state.transactions
    .slice()
    .sort((a, b) => new Date(a.timestamp || 0) - new Date(b.timestamp || 0))
    .slice(-7)
    .map((tx) => ({
      label: (tx.description || tx.category || "tx").slice(0, 6),
      value: Number(tx.amount || 0)
    }));
  drawLineChart(el.trendChart, recentTrend, { emptyTitle: "No recent trend yet" });
}

function parseQueryString(queryText) {
  const params = new URLSearchParams();
  if (!queryText.trim()) return params;
  queryText.split("&").forEach((pair) => {
    const [key, value = ""] = pair.split("=");
    if (key) params.append(key, value);
  });
  return params;
}

async function apiRequest(method, path, options = {}) {
  const url = new URL(path.replace(/^\/+/, ""), `${state.baseUrl.replace(/\/$/, "")}/`);
  if (options.params) {
    const params = options.params instanceof URLSearchParams ? options.params : new URLSearchParams(options.params);
    params.forEach((value, key) => url.searchParams.append(key, value));
  }

  const headers = new Headers(options.headers || {});
  if (state.token && !options.skipAuth) {
    headers.set("Authorization", `Bearer ${state.token}`);
  }

  let body = options.body;
  if (options.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(options.json);
  }
  if (options.form instanceof URLSearchParams) {
    headers.set("Content-Type", "application/x-www-form-urlencoded");
    body = options.form.toString();
  }

  const response = await fetch(url.toString(), { method, headers, body });
  const contentType = response.headers.get("content-type") || "";
  let data;
  if (contentType.includes("application/json")) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  const record = {
    time: new Date().toLocaleTimeString(),
    method,
    path: `${path}${url.search ? url.search : ""}`,
    status: response.status,
    ok: response.ok
  };
  state.apiHistory.unshift(record);
  state.apiHistory = state.apiHistory.slice(0, 20);
  state.lastResponse = { status: response.status, path: record.path, data };
  persistState();
  renderApiHistory();

  if (!response.ok) {
    const detail = typeof data === "string" ? data : data?.detail || JSON.stringify(data);
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return data;
}

function ensureAuthenticated(message = "Login first to use this action.") {
  if (state.token) return true;
  showToast(message, "warning");
  setAuthBanner("Login is required before calling protected endpoints.", "warning");
  return false;
}

async function refreshCurrentUser() {
  if (!state.token) return;
  try {
    const user = await apiRequest("GET", "/users/me");
    state.user = user;
    state.userId = user.id;
    setAuthBanner(`Logged in as ${user.username}. user_id fetched from /users/me.`, "success");
  } catch (error) {
    state.user = null;
    state.userId = null;
    setAuthBanner(`Could not fetch /users/me: ${error.message}`, "warning");
  }
  renderSession();
}

async function fetchAccounts({ silent = false } = {}) {
  if (!ensureAuthenticated()) return [];
  try {
    const accounts = await apiRequest("GET", "/accounts/");
    state.accounts = Array.isArray(accounts) ? accounts : [];
    syncSelectedAccount();
    renderAccounts();
    renderSession();
    if (!silent) showToast("Accounts refreshed.", "success");
    return state.accounts;
  } catch (error) {
    if (!silent) showToast(error.message, "error");
    return [];
  }
}

function syncSelectedAccount() {
  const exists = state.accounts.some((account) => Number(account.id) === Number(state.selectedAccountId));
  if (!exists) {
    state.selectedAccountId = state.accounts.length ? Number(state.accounts[0].id) : null;
  }
  persistState();
}
async function fetchTransactions({ silent = false } = {}) {
  if (!ensureAuthenticated()) return [];
  if (!state.selectedAccountId) {
    renderTransactions();
    return [];
  }

  try {
    const transactions = await apiRequest("GET", `/transactions/account/${state.selectedAccountId}`);
    state.transactions = Array.isArray(transactions) ? transactions : [];
    renderTransactions();
    renderSession();
    if (!silent) showToast("Transactions refreshed.", "success");
    return state.transactions;
  } catch (error) {
    state.transactions = [];
    renderTransactions();
    if (!silent) showToast(error.message, "error");
    return [];
  }
}

async function refreshSessionData() {
  if (!state.token) return;
  setLoading(true, "Refreshing session data...");
  await refreshCurrentUser();
  await fetchAccounts({ silent: true });
  await fetchTransactions({ silent: true });
  setLoading(false);
  showToast("Session data refreshed.", "success");
}

function setSelectedAccount(accountId) {
  state.selectedAccountId = accountId ? Number(accountId) : null;
  persistState();
  renderSession();
  renderAccounts();
  renderTransactions();
}

function switchAuthView(viewName) {
  document.querySelectorAll(".auth-tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.authView === viewName);
  });
  document.querySelectorAll(".auth-view").forEach((view) => {
    view.classList.toggle("active", view.id === `${viewName}View`);
  });
}

async function switchTab(tabName) {
  state.activeTab = tabName;
  persistState();
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tabName);
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.tabPanel === tabName);
  });
  el.pageTitle.textContent = tabName === "api-lab" ? "API Lab" : `${tabName.charAt(0).toUpperCase()}${tabName.slice(1)}`;

  if (tabName === "accounts" && state.token && !state.accounts.length) {
    await fetchAccounts({ silent: true });
  }
  if (tabName === "transactions") {
    if (state.token && !state.accounts.length) await fetchAccounts({ silent: true });
    if (state.token && state.selectedAccountId) await fetchTransactions({ silent: true });
  }
  if (window.innerWidth <= 920) {
    el.sidebar.classList.remove("open");
  }
  renderCharts();
}

function renderSession() {
  el.backendUrlInput.value = state.baseUrl;
  el.activeBackendUrl.textContent = state.baseUrl;

  const userName = state.user?.username || "Guest";
  const userEmail = state.user?.email || (state.token ? "Session active" : "Not logged in");
  const avatar = userName.slice(0, 2).toUpperCase();

  el.sidebarUserName.textContent = userName;
  el.sidebarUserEmail.textContent = userEmail;
  el.sidebarUserId.textContent = state.userId ?? "-";
  el.sidebarAccountId.textContent = state.selectedAccountId ?? "-";
  el.sidebarAvatar.textContent = avatar;

  el.metricUser.textContent = userName;
  el.metricUserSub.textContent = state.user ? userEmail : "Login to fetch /users/me";
  el.metricUserId.textContent = state.userId ?? "-";
  el.metricAccountId.textContent = state.selectedAccountId ?? "-";
  el.metricAccountSub.textContent = state.selectedAccountId ? "Selected from Accounts section" : "Select inside Accounts";
  el.metricTxCount.textContent = String(state.transactions.length);

  el.dashboardAccountCount.textContent = String(state.accounts.length);
  el.accountActionSelectedId.textContent = state.selectedAccountId ?? "-";
  el.transactionCurrentAccountId.textContent = state.selectedAccountId ?? "-";

  const totalBalance = state.accounts.reduce((sum, account) => sum + Number(account.balance || 0), 0);
  el.dashboardBalance.textContent = formatCurrency(totalBalance);

  // Calculate income and expense - normalize transaction_type comparison
  const income = state.transactions
    .filter((tx) => {
      const txType = String(tx.transaction_type || "").toLowerCase().trim();
      return txType === "income";
    })
    .reduce((sum, tx) => sum + Number(tx.amount || 0), 0);
  
  const expense = state.transactions
    .filter((tx) => {
      const txType = String(tx.transaction_type || "").toLowerCase().trim();
      return txType === "expense";
    })
    .reduce((sum, tx) => sum + Number(tx.amount || 0), 0);

  el.dashboardIncome.textContent = formatCurrency(income);
  el.dashboardExpense.textContent = formatCurrency(expense);

  el.appShell.classList.toggle("hidden", !state.token);
  el.authShell.classList.toggle("hidden", Boolean(state.token));
  renderCharts();
}

function renderAccounts() {
  syncSelectedAccount();
  if (!state.accounts.length) {
    el.accountsGrid.className = "account-grid empty-shell";
    el.accountsGrid.innerHTML = "<p>No accounts loaded yet. Use refresh or create your first account.</p>";
  } else {
    el.accountsGrid.className = "account-grid";
    el.accountsGrid.innerHTML = state.accounts.map((account) => {
      const selected = Number(account.id) === Number(state.selectedAccountId);
      return `
        <article class="account-card ${selected ? "selected" : ""}" data-account-id="${account.id}">
          <div class="account-pill">${account.account_type}</div>
          <div>
            <strong>${account.account_name}</strong>
            <p class="account-balance">${formatCurrency(account.balance)}</p>
          </div>
          <div class="account-meta">
            <span>account_id: ${account.id}</span>
            <span>user_id: ${account.user_id}</span>
          </div>
        </article>`;
    }).join("");
  }

  const accountOptions = state.accounts.length
    ? state.accounts.map((account) => `<option value="${account.id}" ${Number(account.id) === Number(state.selectedAccountId) ? "selected" : ""}>${account.id} - ${account.account_name} (${account.account_type})</option>`).join("")
    : '<option value="">No accounts</option>';
  el.transactionAccountSelect.innerHTML = accountOptions;

  renderDashboardTransactions();
  renderCharts();
}

function renderDashboardTransactions() {
  if (!state.transactions.length) {
    el.dashboardTransactions.className = "stack-list empty-shell";
    el.dashboardTransactions.innerHTML = "<p>No transactions loaded yet for the current account.</p>";
    return;
  }

  // Sort transactions by timestamp (latest first)
  const sortedTransactions = [...state.transactions].sort((a, b) => {
    const dateA = new Date(a.timestamp || 0).getTime();
    const dateB = new Date(b.timestamp || 0).getTime();
    return dateB - dateA;
  });

  el.dashboardTransactions.className = "stack-list";
  el.dashboardTransactions.innerHTML = sortedTransactions.slice(0, 5).map((tx) => `
    <article class="transaction-card">
      <header>
        <span>${tx.transaction_type}</span>
        <strong class="transaction-amount ${tx.transaction_type}">${formatCurrency(tx.amount)}</strong>
      </header>
      <div><strong>${tx.description || "No description"}</strong></div>
      <small>${tx.category || "uncategorized"} · ${formatDate(tx.timestamp)}</small>
    </article>`).join("");
}
function getFilteredTransactions() {
  const typeFilter = el.filterTypeInput.value || "all";
  const categoryFilter = el.filterCategoryInput.value || "all";
  
  const filtered = state.transactions.filter((tx) => {
    const typeMatch = typeFilter === "all" || tx.transaction_type === typeFilter;
    const categoryMatch = categoryFilter === "all" || tx.category === categoryFilter;
    return typeMatch && categoryMatch;
  });

  // Sort by timestamp (latest first)
  return filtered.sort((a, b) => {
    const dateA = new Date(a.timestamp || 0).getTime();
    const dateB = new Date(b.timestamp || 0).getTime();
    return dateB - dateA;
  });
}

function renderTransactions() {
  const categories = [...new Set(state.transactions.map((tx) => tx.category).filter(Boolean))];
  const currentCategory = el.filterCategoryInput.value || "all";
  el.filterCategoryInput.innerHTML = ['<option value="all">all</option>']
    .concat(categories.map((category) => `<option value="${category}">${category}</option>`))
    .join("");
  if (categories.includes(currentCategory)) {
    el.filterCategoryInput.value = currentCategory;
  }

  const visibleTransactions = getFilteredTransactions();
  const income = visibleTransactions.filter((tx) => tx.transaction_type === "income").reduce((sum, tx) => sum + Number(tx.amount || 0), 0);
  const expense = visibleTransactions.filter((tx) => tx.transaction_type === "expense").reduce((sum, tx) => sum + Number(tx.amount || 0), 0);
  el.txIncomeTotal.textContent = formatCurrency(income);
  el.txExpenseTotal.textContent = formatCurrency(expense);

  if (!state.selectedAccountId) {
    el.transactionsList.className = "stack-list empty-shell";
    el.transactionsList.innerHTML = "<p>Select an account in Accounts to drive transaction testing.</p>";
    return;
  }

  if (!visibleTransactions.length) {
    el.transactionsList.className = "stack-list empty-shell";
    el.transactionsList.innerHTML = "<p>No transactions match the current filters.</p>";
    return;
  }

  el.transactionsList.className = "stack-list";
  el.transactionsList.innerHTML = visibleTransactions.map((tx) => `
    <article class="transaction-card">
      <header>
        <span>transaction_id: ${tx.id}</span>
        <strong class="transaction-amount ${tx.transaction_type}">${formatCurrency(tx.amount)}</strong>
      </header>
      <div><strong>${tx.description || "No description"}</strong></div>
      <small>${tx.transaction_type} · ${tx.category || "uncategorized"} · ${formatDate(tx.timestamp)}</small>
    </article>`).join("");
  renderCharts();
}

function renderChatLog(target) {
  const logElement = target === "accounts" ? el.accountsChatLog : el.transactionsChatLog;
  const entries = state.chatHistory[target];
  if (!entries.length) {
    logElement.className = "chat-log empty-shell";
    logElement.innerHTML = `<p>Ask a question to test <code>/chat/chat</code> from the ${target} section.</p>`;
    return;
  }

  logElement.className = "chat-log";
  logElement.innerHTML = entries.slice().reverse().map((entry) => {
    const answer = entry.answer;
    let answerMarkup = `<pre class="output-box">${escapeHtml(formatJson(answer))}</pre>`;
    if (answer && Array.isArray(answer.answer)) {
      answerMarkup = `<ul class="chat-answer-list">${answer.answer.map((item) => `<li><strong>${escapeHtml(item.question || "Question")}</strong><div>${escapeHtml(formatJson(item.answer))}</div></li>`).join("")}</ul>`;
    }
    return `
      <article class="chat-entry">
        <header>
          <span>${escapeHtml(entry.question)}</span>
          <strong>${entry.status}</strong>
        </header>
        ${answerMarkup}
      </article>`;
  }).join("");
}

function renderApiHistory() {
  el.apiConsoleOutput.textContent = state.lastResponse ? formatJson(state.lastResponse) : "Responses from the API console will appear here.";
  if (!state.apiHistory.length) {
    el.apiHistory.className = "history-list empty-shell";
    el.apiHistory.innerHTML = "<p>No API calls yet.</p>";
    return;
  }

  el.apiHistory.className = "history-list";
  el.apiHistory.innerHTML = state.apiHistory.map((entry) => `
    <article class="history-item">
      <header>
        <span>${entry.time}</span>
        <strong class="${entry.ok ? "status-success" : "status-error"}">${entry.status}</strong>
      </header>
      <div><strong>${entry.method}</strong> ${escapeHtml(entry.path)}</div>
    </article>`).join("");
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

async function handleLogin(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  setLoading(true, "Logging in...");
  try {
    const params = new URLSearchParams({
      username: String(form.get("username") || ""),
      password: String(form.get("password") || "")
    });
    const data = await apiRequest("POST", "/login", { form: params, skipAuth: true });
    state.token = data.access_token;
    persistState();
    await refreshCurrentUser();
    renderSession();
    await fetchAccounts({ silent: true });
    await fetchTransactions({ silent: true });
    showToast("Login successful.", "success");
    setStatus("Authenticated");
    switchTab("dashboard");
  } catch (error) {
    showToast(error.message, "error");
    setAuthBanner(`Login failed: ${error.message}`, "error");
  } finally {
    setLoading(false);
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  setLoading(true, "Creating user...");
  try {
    const payload = {
      username: String(form.get("username") || ""),
      email: String(form.get("email") || ""),
      password: String(form.get("password") || "")
    };
    const data = await apiRequest("POST", "/users/", { json: payload, skipAuth: true });
    setAuthBanner(`Account created. Check email for OTP. ${typeof data === "string" ? data : ""}`.trim(), "success");
    showToast("User created. Verify OTP next.", "success");
    switchAuthView("verify");
    document.getElementById("verifyEmail").value = payload.email;
  } catch (error) {
    showToast(error.message, "error");
    setAuthBanner(`Registration failed: ${error.message}`, "error");
  } finally {
    setLoading(false);
  }
}

async function handleVerify(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  setLoading(true, "Verifying email...");
  try {
    await apiRequest("POST", "/users/verify-email", {
      json: {
        email: String(form.get("email") || ""),
        otp: String(form.get("otp") || "")
      },
      skipAuth: true
    });
    setAuthBanner("Email verified successfully. You can log in now.", "success");
    showToast("Email verified.", "success");
    switchAuthView("login");
  } catch (error) {
    showToast(error.message, "error");
    setAuthBanner(`Verification failed: ${error.message}`, "error");
  } finally {
    setLoading(false);
  }
}
async function handleResendOtp() {
  if (!ensureAuthenticated("Login first, then resend OTP if needed.")) return;
  setLoading(true, "Resending OTP...");
  try {
    const data = await apiRequest("POST", "/users/resend-otp");
    setAuthBanner(typeof data === "string" ? data : data.detail || "OTP resent successfully.", "success");
    showToast("OTP resent.", "success");
  } catch (error) {
    showToast(error.message, "error");
    setAuthBanner(`Resend OTP failed: ${error.message}`, "error");
  } finally {
    setLoading(false);
  }
}

function logout() {
  state.token = null;
  state.user = null;
  state.userId = null;
  state.accounts = [];
  state.transactions = [];
  state.selectedAccountId = null;
  state.activeTab = "dashboard";
  persistState();
  renderSession();
  renderAccounts();
  renderTransactions();
  renderChatLog("accounts");
  renderChatLog("transactions");
  
  // Reset UI elements
  el.sidebarUserName.textContent = "Guest";
  el.sidebarUserEmail.textContent = "Not logged in";
  el.sidebarUserId.textContent = "-";
  el.sidebarAccountId.textContent = "-";
  el.sidebarAvatar.textContent = "FA";
  
  showToast("✅ Logged out successfully. You can now login or register.", "success");
  setStatus("Ready");
  
  // Optional: Clear auth view select
  document.querySelectorAll(".auth-tab").forEach(tab => tab.classList.remove("active"));
  document.querySelectorAll(".auth-view").forEach(view => view.classList.remove("active"));
  document.querySelector('[data-auth-view="login"]').classList.add("active");
  document.getElementById("loginView").classList.add("active");
}

async function handleCreateAccount(event) {
  event.preventDefault();
  if (!ensureAuthenticated()) return;
  setLoading(true, "Creating account...");
  try {
    const payload = {
      account_details: {
        account_name: document.getElementById("accountNameInput").value.trim(),
        account_type: document.getElementById("accountTypeInput").value,
        balance: 0
      },
      initial_transaction: {
        transaction_type: "income",
        amount: Number(document.getElementById("accountAmountInput").value || 0),
        description: document.getElementById("accountDescriptionInput").value.trim(),
        category: document.getElementById("accountCategoryInput").value,
        timestamp: null
      }
    };
    const data = await apiRequest("POST", "/accounts/", { json: payload });
    el.accountActionOutput.textContent = formatJson(data);
    document.getElementById("accountForm").reset();
    document.getElementById("accountTypeInput").value = "checking";
    document.getElementById("accountCategoryInput").value = "other";
    document.getElementById("accountDescriptionInput").value = "Initial deposit";
    el.accountFormCard.classList.add("hidden");
    await fetchAccounts({ silent: true });
    await fetchTransactions({ silent: true });
    showToast("Account created.", "success");
  } catch (error) {
    showToast(error.message, "error");
    el.accountActionOutput.textContent = error.message;
  } finally {
    setLoading(false);
  }
}

async function runAccountAction(kind) {
  if (!ensureAuthenticated()) return;
  if (!state.selectedAccountId) {
    showToast("Select an account first.", "warning");
    return;
  }

  const routes = {
    details: `/accounts/${state.selectedAccountId}`,
    summary: `/accounts/summary/${state.selectedAccountId}`,
    balance: `/accounts/summmary/${state.selectedAccountId}/balance`
  };

  setLoading(true, `Fetching account ${kind}...`);
  try {
    const data = await apiRequest("GET", routes[kind]);
    el.accountActionOutput.textContent = formatJson(data);
    showToast(`Account ${kind} loaded.`, "success");
  } catch (error) {
    el.accountActionOutput.textContent = error.message;
    showToast(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function deleteSelectedAccount() {
  if (!ensureAuthenticated()) return;
  if (!state.selectedAccountId) {
    showToast("Select an account first.", "warning");
    return;
  }
  const ok = window.confirm(`Delete account ${state.selectedAccountId}? This also deletes its transactions.`);
  if (!ok) return;

  setLoading(true, "Deleting account...");
  try {
    const data = await apiRequest("DELETE", `/accounts/delete/${state.selectedAccountId}`);
    el.accountActionOutput.textContent = formatJson(data);
    state.selectedAccountId = null;
    await fetchAccounts({ silent: true });
    await fetchTransactions({ silent: true });
    showToast("Account deleted.", "success");
  } catch (error) {
    el.accountActionOutput.textContent = error.message;
    showToast(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function handleCreateTransaction(event) {
  event.preventDefault();
  if (!ensureAuthenticated()) return;
  if (!state.selectedAccountId) {
    showToast("Select an account before creating a transaction.", "warning");
    return;
  }

  setLoading(true, "Creating transaction...");
  try {
    const payload = {
      transaction_type: document.getElementById("transactionTypeInput").value,
      amount: Number(document.getElementById("transactionAmountInput").value || 0),
      description: document.getElementById("transactionDescriptionInput").value.trim(),
      category: document.getElementById("transactionCategoryInput").value,
      timestamp: null
    };
    const data = await apiRequest("POST", "/transactions/", {
      params: { account_id: state.selectedAccountId },
      json: payload
    });
    el.transactionActionOutput.textContent = formatJson(data);
    el.transactionFormCard.classList.add("hidden");
    await fetchTransactions({ silent: true });
    await fetchAccounts({ silent: true });
    showToast("Transaction created.", "success");
  } catch (error) {
    el.transactionActionOutput.textContent = error.message;
    showToast(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function getTransactionById() {
  const transactionId = Number(document.getElementById("transactionIdInput").value || 0);
  if (!transactionId) {
    showToast("Enter a transaction ID.", "warning");
    return;
  }
  setLoading(true, "Fetching transaction...");
  try {
    const data = await apiRequest("GET", `/transactions/${transactionId}`);
    el.transactionActionOutput.textContent = formatJson(data);
    showToast("Transaction loaded.", "success");
  } catch (error) {
    el.transactionActionOutput.textContent = error.message;
    showToast(error.message, "error");
  } finally {
    setLoading(false);
  }
}
async function updateTransactionById() {
  const transactionId = Number(document.getElementById("transactionIdInput").value || 0);
  if (!transactionId) {
    showToast("Enter a transaction ID.", "warning");
    return;
  }

  const payload = {};
  const amount = document.getElementById("updateAmountInput").value;
  const type = document.getElementById("updateTypeInput").value;
  const category = document.getElementById("updateCategoryInput").value;
  const description = document.getElementById("updateDescriptionInput").value.trim();
  if (amount !== "") payload.amount = Number(amount);
  if (type) payload.transaction_type = type;
  if (category) payload.category = category;
  if (description) payload.description = description;

  setLoading(true, "Updating transaction...");
  try {
    const data = await apiRequest("PUT", `/transactions/${transactionId}`, { json: payload });
    el.transactionActionOutput.textContent = formatJson(data);
    await fetchTransactions({ silent: true });
    await fetchAccounts({ silent: true });
    showToast("Transaction updated.", "success");
  } catch (error) {
    el.transactionActionOutput.textContent = error.message;
    showToast(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function deleteTransactionById() {
  const transactionId = Number(document.getElementById("transactionIdInput").value || 0);
  if (!transactionId) {
    showToast("Enter a transaction ID.", "warning");
    return;
  }
  const ok = window.confirm(`Delete transaction ${transactionId}?`);
  if (!ok) return;

  setLoading(true, "Deleting transaction...");
  try {
    const data = await apiRequest("DELETE", `/transactions/${transactionId}`);
    el.transactionActionOutput.textContent = formatJson(data);
    await fetchTransactions({ silent: true });
    await fetchAccounts({ silent: true });
    showToast("Transaction deleted.", "success");
  } catch (error) {
    el.transactionActionOutput.textContent = error.message;
    showToast(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function sendChat(target, promptText) {
  if (!ensureAuthenticated("Login first to use chatbot.")) return;
  const prompt = promptText.trim();
  if (!prompt) {
    showToast("Enter a prompt first.", "warning");
    return;
  }

  setLoading(true, "Sending chat request...");
  try {
    const data = await apiRequest("POST", "/chat/chat", { params: { user_input: prompt } });
    state.chatHistory[target].push({ question: prompt, answer: data, status: "ok" });
    persistState();
    renderChatLog(target);
    showToast("Chat response received.", "success");
  } catch (error) {
    state.chatHistory[target].push({ question: prompt, answer: error.message, status: "error" });
    persistState();
    renderChatLog(target);
    showToast(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function handleApiConsole(event) {
  event.preventDefault();
  const method = el.apiMethodInput.value;
  const path = el.apiPathInput.value.trim();
  const params = parseQueryString(el.apiParamsInput.value);
  const rawBody = el.apiBodyInput.value.trim();
  const options = {};
  if (params.toString()) options.params = params;

  if (method !== "GET" && rawBody) {
    try {
      options.json = JSON.parse(rawBody);
    } catch (error) {
      showToast("JSON body is invalid.", "error");
      return;
    }
  }

  setLoading(true, `Sending ${method} request...`);
  try {
    const data = await apiRequest(method, path, options);
    el.apiConsoleOutput.textContent = formatJson(data);
    showToast("Request completed.", "success");
  } catch (error) {
    el.apiConsoleOutput.textContent = error.message;
    showToast(error.message, "error");
  } finally {
    setLoading(false);
  }
}

function downloadApiHistory() {
  const blob = new Blob([JSON.stringify(state.apiHistory, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `api-history-${new Date().toISOString().replace(/[:.]/g, "-")}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function bindEvents() {
  document.querySelectorAll(".auth-tab").forEach((tab) => {
    tab.addEventListener("click", () => switchAuthView(tab.dataset.authView));
  });
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => switchTab(button.dataset.tab));
  });
  document.querySelectorAll(".prompt-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const target = chip.dataset.chatTarget;
      const prompt = chip.dataset.prompt || "";
      if (target === "accounts") {
        el.accountsChatInput.value = prompt;
      } else {
        el.transactionsChatInput.value = prompt;
      }
      sendChat(target, prompt);
    });
  });

  document.getElementById("saveBackendUrlBtn").addEventListener("click", () => {
    state.baseUrl = el.backendUrlInput.value.trim() || state.baseUrl;
    persistState();
    renderSession();
    showToast("Backend URL saved.", "success");
  });
  document.getElementById("loginForm").addEventListener("submit", handleLogin);
  document.getElementById("registerForm").addEventListener("submit", handleRegister);
  document.getElementById("verifyForm").addEventListener("submit", handleVerify);
  document.getElementById("resendOtpBtn").addEventListener("click", handleResendOtp);
  document.getElementById("logoutBtn").addEventListener("click", logout);
  document.getElementById("quickRefreshBtn").addEventListener("click", refreshSessionData);
  document.getElementById("refreshDashboardBtn").addEventListener("click", refreshSessionData);
  document.getElementById("openApiLabBtn").addEventListener("click", () => switchTab("api-lab"));
  document.getElementById("refreshAccountsBtn").addEventListener("click", () => fetchAccounts());
  document.getElementById("toggleAccountFormBtn").addEventListener("click", () => el.accountFormCard.classList.toggle("hidden"));
  document.getElementById("cancelAccountFormBtn").addEventListener("click", () => el.accountFormCard.classList.add("hidden"));
  document.getElementById("accountForm").addEventListener("submit", handleCreateAccount);
  document.getElementById("getAccountDetailsBtn").addEventListener("click", () => runAccountAction("details"));
  document.getElementById("getAccountSummaryBtn").addEventListener("click", () => runAccountAction("summary"));
  document.getElementById("getAccountBalanceBtn").addEventListener("click", () => runAccountAction("balance"));
  document.getElementById("deleteAccountBtn").addEventListener("click", deleteSelectedAccount);
  document.getElementById("accountsChatForm").addEventListener("submit", (event) => {
    event.preventDefault();
    sendChat("accounts", el.accountsChatInput.value);
    el.accountsChatInput.value = "";
  });
  document.getElementById("transactionsChatForm").addEventListener("submit", (event) => {
    event.preventDefault();
    sendChat("transactions", el.transactionsChatInput.value);
    el.transactionsChatInput.value = "";
  });
  document.getElementById("toggleTransactionFormBtn").addEventListener("click", () => el.transactionFormCard.classList.toggle("hidden"));
  document.getElementById("cancelTransactionFormBtn").addEventListener("click", () => el.transactionFormCard.classList.add("hidden"));
  document.getElementById("transactionForm").addEventListener("submit", handleCreateTransaction);
  document.getElementById("refreshTransactionsBtn").addEventListener("click", () => fetchTransactions());
  document.getElementById("transactionAccountSelect").addEventListener("change", async (event) => {
    setSelectedAccount(event.target.value);
    await fetchTransactions({ silent: true });
  });
  el.filterTypeInput.addEventListener("change", renderTransactions);
  el.filterCategoryInput.addEventListener("change", renderTransactions);
  document.getElementById("getTransactionBtn").addEventListener("click", getTransactionById);
  document.getElementById("updateTransactionBtn").addEventListener("click", updateTransactionById);
  document.getElementById("deleteTransactionBtn").addEventListener("click", deleteTransactionById);
  document.getElementById("apiConsoleForm").addEventListener("submit", handleApiConsole);
  document.getElementById("downloadHistoryBtn").addEventListener("click", downloadApiHistory);
  document.getElementById("sidebarToggle").addEventListener("click", () => el.sidebar.classList.toggle("open"));

  el.accountsGrid.addEventListener("click", async (event) => {
    const card = event.target.closest("[data-account-id]");
    if (!card) return;
    setSelectedAccount(card.dataset.accountId);
    await fetchTransactions({ silent: true });
  });

  window.addEventListener("resize", () => {
    renderCharts();
  });
}

async function bootstrap() {
  cacheElements();
  hydrateState();
  bindEvents();
  renderSession();
  renderAccounts();
  renderTransactions();
  renderChatLog("accounts");
  renderChatLog("transactions");
  renderApiHistory();
  renderCharts();
  el.backendUrlInput.value = state.baseUrl;
  setStatus(state.token ? "Restoring session" : "Ready");

  if (state.token) {
    await refreshCurrentUser();
    await fetchAccounts({ silent: true });
    await fetchTransactions({ silent: true });
    switchTab(state.activeTab);
    setStatus("Authenticated");
  }
}

document.addEventListener("DOMContentLoaded", bootstrap);




