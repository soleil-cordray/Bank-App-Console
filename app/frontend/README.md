# ABC Digital Bank: React Frontend

The web frontend for the Bank-App FastAPI backend. Customers check balances and
send money; branch managers and admins see branch analytics.

Built with **React 19**, **Material-UI 9**, **React Router 8**, **axios**, and **Vite 8**.
Module: *07 – React Frontend, Connect with Backend*.

---

## Features

| Who | Can do |
|---|---|
| Everyone | Log in / log out, stay logged in across refreshes, auto-logout when the token expires |
| `CUSTOMER` | See own accounts and recent transactions, transfer money |
| `BRANCH_MANAGER` | See all accounts, **Analytics** for their own branch |
| `ADMIN` | Everything above, plus a **branch picker** on Analytics |

**Analytics** shows, for a chosen branch and month:
- transaction volume, transaction count, and staff headcount (direct vs. contract)
- the branch's staff list, with the manager tagged
- monthly transfer volume for every branch
- branches over a staff-per-manager limit, and over a contract-staff percentage (both adjustable)

Every page works on phones and shows the backend's own error messages
(e.g. *"A single transfer can't be more than 10000.00."*).

---

## Getting started

### Prerequisites

- **Node.js 20+** (`node --version`)
- **Python venv** for the backend, with `requirements.txt` installed
- **MongoDB** running locally (or via `docker compose up mongo`)
- A `.env` in the project root with `MONGO_URI`, `DB_NAME`, `JWT_SECRET`

### 1. Backend (terminal 1, project root)

```bash
venv\Scripts\activate              # macOS/Linux: source venv/bin/activate
python -m app.seed_demo            # once: demo branch, customers, accounts, logins
python -m app.create_admin         # once, optional: an ADMIN login (you choose the password)
uvicorn app.main:app --reload      # http://127.0.0.1:8000  (Swagger at /docs)
```

### 2. Frontend (terminal 2)

```bash
cd frontend
npm install                        # once, and after anyone changes package.json
npm run dev                        # http://localhost:5173
```

### 3. Log in

| Login | Role | What to look at |
|---|---|---|
| `demo.customer@bank.test` | CUSTOMER | 2 accounts, history, Transfer page |
| `demo.friend@bank.test` | CUSTOMER | account `0000000003`, a transfer target |
| `demo.manager@bank.test` | BRANCH_MANAGER | Analytics for branch DEMO-01 |
| `demo.teller@bank.test` | TELLER | dashboard only (no teller page yet) |
| your admin | ADMIN | every page, branch picker on Analytics |

Demo password: see the top of [`app/seed_demo.py`](../app/seed_demo.py).
Demo logins are for **local development only**.

> **Tip:** to see the admin branch picker with more than one branch, create a
> second branch in Swagger (`POST /branches`, authorized as your admin).

---

## How it works

```
Browser ──> Vite dev server :5173 ──/api/*──> FastAPI :8000 ──> MongoDB
             (proxy in vite.config.js)
```

- **Proxy, not CORS.** In development, Vite forwards `/api/*` to FastAPI, so the
  browser sees one site and the backend needs no CORS settings.
- **Login** posts a *form* (`username` + `password`) to `/auth/login`, saves the
  JWT in `localStorage`, then calls `/auth/me` to learn the user's role.
- **Every request** gets `Authorization: Bearer <token>` from an axios interceptor.
  A `401` clears the token and sends the user to `/login?expired=1`.
- **Roles** decide which links and pages are *shown* (`auth/roles.js`,
  `ProtectedRoute`). The backend's `require_roles` still enforces access.

### Project structure

```
frontend/
├── index.html                the one HTML page; React fills <div id="root">
├── vite.config.js            dev server + /api proxy
├── package.json              dependencies + npm scripts
└── src/
    ├── main.jsx              entry: theme, router, auth provider
    ├── App.jsx               routes: URL -> page, and who may open it
    ├── theme.js              colors and shapes for the whole app
    ├── api/
    │   ├── client.js         axios instance, JWT + 401 interceptors, getErrorMessage()
    │   └── useApi.js         hook: useApi('/url') -> { data, error, loading }
    ├── auth/
    │   ├── AuthContext.jsx   login(), logout(), current user via useAuth()
    │   └── roles.js          role groups (mirror app/dependencies.py)
    ├── components/
    │   ├── NavBar.jsx        top bar; links depend on role
    │   ├── ProtectedRoute.jsx  requires login (and optionally a role)
    │   └── DataTable.jsx     reusable table from columns + rows
    ├── pages/
    │   ├── LoginPage.jsx
    │   ├── DashboardPage.jsx balances + recent transactions
    │   ├── TransferPage.jsx  send money
    │   └── AnalyticsPage.jsx manager / admin dashboard
    └── utils/format.js       formatMoney(), formatDate()
```

### Backend endpoints used

| Page | Endpoints |
|---|---|
| Login | `POST /auth/login`, `GET /auth/me` |
| Dashboard | `GET /accounts`, `GET /transactions` |
| Transfer | `GET /accounts`, `POST /transactions/transfer` |
| Analytics | `GET /branches`, `GET /branches/{id}`, `GET /branches/analytics/transaction-volume`, `/monthly-transfer-volume`, `/staff-to-manager-ratio`, `/non-direct-staff-ratio` |

---

## Scripts

| Command | Does |
|---|---|
| `npm run dev` | dev server with hot reload on :5173 |
| `npm run build` | production build into `dist/` |
| `npm run preview` | serve the `dist/` build locally |

---

## Adding a page (the pattern)

1. Create `src/pages/MyPage.jsx`. Load data with `useApi('/some/endpoint')` and
   show it with `<DataTable>` (see `AnalyticsPage.jsx`).
2. Add a `<Route>` in `App.jsx`, wrapped in `<ProtectedRoute roles={...}>` if needed.
3. Add a link in `NavBar.jsx`, shown only for the right roles.
4. Show errors with `getErrorMessage(err)` and dates with `formatDate()`.

### Next tasks

1. **Transaction history** with Type and Start-date filters
   (`GET /transactions?type=TRANSFER&start_date=2026-09-01`)
2. **Register page:** `POST /auth/register` `{email, password}` (JSON)
3. **Teller page:** deposit / withdraw via `POST /transactions` (role `TELLER`)
4. **Customer name** on the dashboard: `GET /customers/{user.customer_id}`
5. **Phone nav:** MUI `Drawer` instead of buttons on small screens
6. **Admin screens:** customer / branch create-edit-deactivate
7. **Charts** for monthly transfer volume (e.g. `@mui/x-charts`)
8. **Tests** with Vitest + React Testing Library

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "Can't reach the bank server" | Start the backend: `uvicorn app.main:app --reload` |
| "Invalid email or password" for a demo login | Run `python -m app.seed_demo` (against the DB in your `.env`) |
| Bounced to login with "session expired" | Normal after 30 min (`JWT_EXPIRE_MINUTES`); log in again |
| Times look hours off | Always display dates with `formatDate()`; the API sends UTC without a `Z` |
| Every request appears twice in DevTools | React `StrictMode` in development; normal |
| Build warns about a chunk over 500 kB | MUI's size; safe to ignore for now |
| Online examples don't work | They're often for older versions: use `<Grid size={{ xs: 12 }}>` (not `item xs`), and import from `react-router` (not `react-router-dom`) |

## Security notes

- The token lives in `localStorage` for simplicity. Production banking apps use
  httpOnly cookies so injected scripts can't read it.
- Hiding links is not access control; the backend checks roles on every request.

## Deploying (later)

The proxy only exists in `npm run dev`. For a deployment, either serve `dist/`
from the same domain as the API, or add FastAPI's `CORSMiddleware` in
`app/main.py` with the frontend's URL.
