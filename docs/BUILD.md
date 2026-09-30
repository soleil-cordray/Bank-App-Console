# Build Guide

File-specific requirements and build guides. See `DESIGN.md` for design choice elaboration.

#### Contents
1. [Backend](#backend)
    - [`security.py`](#securitypy)
    - [`seed_data.py`](#seed_datapy)
    - [`core.py`](#corepy)
    - [`domain.py`](domainpy)
    - [`lookup.py`](#lookuppy)
    - [`auth.py`](#authpy)
    - [`bank_ops.py`](#bank_opspy)
    - [`analytics_logic.py`](#analytics_logicpy)
    - [`routes/`](#routes)
    - [`main.py`](#mainpy)
    - [`smoke_test.py`](#smoke_testpy)
    - [`demo.sh`](#demosh)
    - [`app/`](#app)
    - [`db.py`](#dbpy)
    - [`repositories/`](#repositories)
    - [`seed_mongo.py`](#seed_mongopy)
2. [Frontend](#frontend)

## Backend

### `security.py`
Password hashing and tokens (rubric 5, **Authentication** section in `DESIGN.md`). Imports nothing from the app, so any file can use it

#### Settings
- `SECRET_KEY` from the environment (a development default of at least 32 characters is fine)
- Algorithm `HS256`
- Token lifetime 60 minutes
- Round 12 bycrypt (read the rounds from the environment so tests can lower it)

#### Methods
- [ ] `hash_password(password)`: Returns a salted bcrypt hash as a string
- [ ] `verify_password(password, hash)`: Returns True or False
- [ ] `create_access_token(claims, expires_minutes)`: Copies the claims and adds `iat` and `exp`; returns a signed JWT
- [ ] `decode_token(token)`: Returns the claims; raises a JWT error if the token is malformed, tampered with, or expired

#### Done When
- [ ] A hash verifies against its own password and not another
- [ ] A token created with `expires_minutes=-1` fails to decode.

---

### `seed_data.py`
The demo data in its own file (rubric 1.1).

#### Lists
- [ ] `accounts` (logins) has:
  ```bash
  id
  username
  password_hash # call hash_password("demo password"))
  account_type # "admin" or "user"
  customer_id # None for the admin
- [ ] `customers` has:
  ```bash
  id
  name
  email
  postal_code
  address
  balance # the main account
  branch_id
  is_active # True
- [ ] `branches` has:
  ```bash
  id
  branch_code # BR-001
  name
  location
  manager_id
  staff # a list of {id, name, role: MANAGER or TELLER, employment_type: DIRECT or CONTRACT}
  ```

#### Done When
- [ ] Importing the file works
- [ ] Every login has a matching customer (except the admin)

---

### `core.py`
The shared file (rubric 1.1, 2.2). Keep edits tiny and push them right away.

#### Requirements
- [ ] Create `app = FastAPI(title="Bank-App Console")` & `api = APIRouter(prefix="/api/v1")`
  - Every route file uses `@api.get(...)` and so on
- [ ] Import the three lists from `seed_data.py` & create `transactions = []`
- [ ] One counter per list, never shared:
  - `account_id_counter` (logins, start after the seed)
  - `customer_id_counter`
  - `bank_account_id_counter` (starts at 1000)
  - `branch_id_counter`
  - `transaction_id_counter`
- [ ] Define these request & response models with Pydantic
- [ ] **No response model contains a password / hash**

#### Models (Fields & Validation)
- [ ] `CustomerCreate` has:
  ```bash
  name # not empty or blank
  email # must look like a@b.c
  username
  password # 8-64 characters
  postal_code
  address
  branch_id # default 1
  initial_balance # at least 0, default 0
  ```
- [ ] `CustomerUpdate` has:
  ```bash
  name # optional (not blank)
  email # valid
  postal_code
  address
  ```
- [ ] `CustomerRead` has:
  ```bash
  name
  email
  postal_code
  address
  balance
  branch_id # no id: customers never see ids
  ```
- [ ] `CustomerAdminRead` has:
  ```bash
  # Everything in `CustomerRead` plus:
  id
  is_active
  ```
- [ ] `AccountOpen` has:
  ```bash
  customer_id
  branch_id
  account_type # CHECKING or SAVINGS (default CHECKING)
  initial_balance # at least 0
  ```
- [ ] `MyAccountOpen` has:
  ```bash
  # Same as AccountOpen, minus customer_id
  branch_id # optional
  ```
- [ ] `AccountView` has:
  ```bash
  id
  account_number
  customer_id
  branch_id
  account_type
  balance
  is_active
  ```
- [ ] `TransactionRequest` has:
  ```bash
  type # DEPOSIT or WITHDRAWAL
  amount # above 0
  bank_account_id # optional; empty means the main account
  ```
- [ ] `TransferRequest` has:
  ```bash
  from_account_id
  to_account_id
  amount # above 0
  ```
- [ ] `TransactionView` has:
  ```bash
  id
  type
  from_account_id
  to_account_id
  amount
  timestamp
  branch_id
  ```
- [ ] `Staff` has:
  ```bash
  id
  name
  role
  employment_type
  ```
- [ ] `BranchWrite` has:
  ```bash
  name
  location # both not empty
  manager_id # optional
  staff # list of Staff, default empty
  ```

#### Done When
- [ ] The models import without errors
- [ ] `api` exists

---

### `domain.py`
OOP account classes (rubric: 1.2). The numbers here are placeholders.

#### Requirements
- [ ] `TRANSFER_LIMIT`: 10,000 (constant)
- [ ] `Account(account_number, customer_id, branch_id, balance)`:
  - Stores balance in `_balance`
  - Private, rounded to cents
- [ ] `get_balance()`: returns `_balance`
- [ ] `deposit(amount)`:
  - Raises `ValueError` if amount is zero/negative
  - Otherwise adds it
- [ ] `_lowest_allowed_balance()`:
  - Returns `0` in `Account`
  - Each subclass overrides it (this is the **polymorphism**)
- [ ] `withdraw(amount)`:
  - Raises `ValueError` if the amount is not positive, or if `_balance - amount` would go below `_lowest_allowed_balance()` ("Insufficient Funds")
  - Otherwise subtracts it
- [ ] `SavingsAccount(Account)`:
  - `MIN_BALANCE = 100`
  - The lowest allowed balance is `MIN_BALANCE`
- [ ] `CheckingAccount(Account)`:
  - `OVERDRAFT_LIMIT = 500`
  - The lowest allowed balance is `-OVERDRAFT_LIMIT`

#### Done When
In a Python shell:
- [ ] A `SavingsAccount` with 500 can withdraw 400 but not 401
- [ ] A `CheckingAccount` with 0 can withdraw 500 but not 501

---

### `lookup.py`
> This will move inside account_repository in Step 12

One flat list of all accounts to allow filtering, transfers, and "customer from account id" to share one code path (rubric 1.1, 1.3, 2.3).

#### Methods
- [ ] `make_account_number(id)`: `ACC-` plus the id zero-padded to 6 digits (`ACC-000001`)
- [ ] `iter_accounts()` where:
  - Yields `(view, source)` pairs
  - First each customer's **main account** (id = customer id, type `CHECKING`, balance and branch from the customer), then each entry in the customer's `bank_accounts`
  - `view`: the *flat* dict used for JSON (an account counts as active only if its customer is active)
  - `source`: the *real* dict whose `balance` gets changed
- [ ] `find_account(id)` where:
  - Returns `(view, source)`
  - Raises `404` "Account not found"
- [ ] `find_accounts(branch_id, min_balance, max_balance, customer_id)`: Start with every view and narrow once per filter that was provided
- [ ] `get_branch_or_404(id)`: Returns the branch; raises `404` "Branch not found"

#### Done When
- [ ] `find_accounts(branch_id=2, min_balance=2000)` returns exactly the seed accounts that match

---

### `auth.py`
Who is calling, and are they allowed? Every route uses these (rubric 2.2).

`oauth2_scheme` is FastAPI's `OAuth2PasswordBearer` with `tokenUrl="/api/v1/auth/token"`. This is also what puts the **Authorize** button in Swagger.

#### Methods
- [ ] `get_customer_or_404(id)`: Returns the customer; raises 404 "Customer not found"
- [ ] `get_current_user(token)` where:
  - Decodes the JWT and returns the matching login
  - A bad, expired, or forged token, or an unknown user, raises `401` with the header `WWW-Authenticate: Bearer`
  - A login whose customer is deactivated raises `403`, so a token issued before a deactivation stops working immediately
- [ ] `customer_only`: Admins get `403`; a customer gets their customer record
- [ ] `admin_only`: Non-admins get `403`; the admin gets their login
- [ ] `owner_or_admin(customer_id)` where:
  - Used on `/customers/{customer_id}/...` routes
  - Allows the admin, or a customer whose own id equals `customer_id`; otherwise `403`

#### Done When
- [ ] A request with no token gets `401`
- [ ] A customer calling an admin-only route gets `403`

---

### `bank_ops.py`

All money movement. Rules live in the account classes, this file applies them (rubric 1.2, 1.4, 2.2).

#### Requirements
- [ ] Use one **reentrant lock** (`threading.RLock`) around every read-modify-write:
  - Ensures two simultaneous withdrawals cannot both pass the balance check
  - Must be reentrant because opening an account deposits while already holding it
- [ ] `to_domain(view)`: builds a `SavingsAccount` or `CheckingAccount` from an account view
- [ ] A `ValueError` from an account class becomes a `400` with its message
- [ ] Every transaction is stored as `{id, type, from_account_id, to_account_id, amount, timestamp, branch_id, customer_id, to_customer_id}` where:
  - `timestamp`: ISO format to the second
  - `branch_id`: the branch of the account the money left (or entered, for a deposit)
  - `customer_id` / `to_customer_id`: who may see it
  - Types: `DEPOSIT`, `WITHDRAWAL`, `TRANSFER`

#### Methods
- [ ] `deposit(customer_id, account_id, amount)` where:
  - Account must:
    - exist (`404`)
    - belong to the caller (`403`)
    - be active (`400`)
  - Applies:
    -  `deposit()`
    - Writes the balance back
  - Logs a `DEPOSIT` (to-account only)
- [ ] `withdraw(customer_id, account_id, amount)` where:
  - Same checks
  - Applies: `withdraw()` (enforces minimum balance and overdraft)
  - Logs a `WITHDRAWAL` (from-account only)
- [ ] `transfer(customer_id, from_id, to_id, amount)` where:
  - Requirements:
    - `400` if same account
    - `400` if over `TRANSFER_LIMIT`
    - Source must be the caller's & active
    - Destination must exist (`404`) and be active (`400`)
  - Applies:
    - Withdraw from the source before anything changes
    - Then deposit to the destination
    - Write both balances
  - Log a `TRANSFER`
- [ ] `open_account(customer, branch_id, account_type, initial_balance)` where:
  - Requirements:
    - `400` if the customer is deactivated
    - `404` if the branch is unknown
    - `400` if a savings account starts below the minimum balance
  - Applies:
    - Creates an extra account (id from `bank_account_id_counter`, balance `0`, active) inside the customer's `bank_accounts`
    - If `initial_balance` is above `0`, deposits it (logged as a `DEPOSIT`)
  - Returns the account view
- [ ] `close_account(account_id)` where:
  - Requirements:
    - `400` for a main account (id below `1000`: deactivate the customer instead)
    - `400` if already closed
    - `400` if overdrawn
  Applies:
    - Pays out the remaining balance as a logged `WITHDRAWAL`
    - Sets balance `0` and inactive (a savings account can never be withdrawn to zero due to minimum, so it would never be closed otherwise)

#### Done When
- [ ] A failed transfer changes no balance
- [ ] 40 simultaneous withdrawals against an account that can afford 30 succeed exactly 30 times.

---

### `analytics_logic.py`
Chapter 1's logic questions in plain Python (rubric 1.3, 3.3). Step 13 turns them into aggregation pipelines; keep these as the reference answers.

#### Methods
- [ ] `transfer_volume_by_branch(month)` where:
  - Month is `YYYY-MM`
  - Sum the `amount` of `TRANSFER` transactions whose timestamp starts with the month, grouped by each transaction's `branch_id`
  - Returns `[{branch_id, month, total_transferred}]` sorted by branch
- [ ] `branches_over_staff_manager_ratio(limit)` where:
  - For each branch:
    - managers = staff with role `MANAGER`
    - others = the rest
    - ratio = others divided by managers, rounded to 2 places
  - Include branches with ratio above `limit` as `{branch_id, branch_code, ratio}`
  - A branch with staff but **no manager** is included with `ratio: null` and `note: "no manager"` (never divide by zero, & infinity is not valid JSON)
- [ ] `branches_over_contract_ratio(threshold=0.20)` where:
  - Skip branches with no staff
  - ratio = `CONTRACT` staff divided by all staff
  - Include branches strictly above the threshold as `{branch_id, branch_code, contract_ratio}` (exactly 20 percent is not included)

#### Done When
- [ ] Seeded branch appears in the contract-ratio and staff-ratio results, and the other does not

---

### `route/`

FILE STRUCTURE CHANGED. UPDATE.

---

### `main.py`

The entry point (rubric 2.2)

#### Steps
1. Import `app` and `api` from `core`
2. Import every `route` file, one line each (`import routes.customers.create`, and so on).
   - Importing a file is what registers its routes; forgotten import means silent `404`
3. Call `app.include_router(api)` after all the imports and route definitions
4. Add `GET /` returning a short hello message
5. Add a handler for `RequestValidationError` that returns `400` (FastAPI's default is `422`)
6. Add a catch-all handler for `Exception` that returns `500` `{"detail": "Internal server error"}`
7. Add a demo-only route `GET /api/v1/debug/error` (before `include_router`) that raises an exception, so you can show a real `500`

#### Done When
- [ ] `/docs` lists every endpoint under `/api/v1`
- [ ] The debug route returns `500`

---

###
