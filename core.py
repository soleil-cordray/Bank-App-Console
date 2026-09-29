# [EXPLAIN] core.py is the shared foundation: the FastAPI app, the in-memory data, the ID counters, and the request models. Every route file imports from here.
# [SUGGEST] Everyone will touch this file eventually, so it is the likeliest place for merge conflicts. Later, consider splitting it (schemas.py for models, database.py for data), but only after this split settles.
# [SUGGEST] HTTPException is no longer used in this file (the route files import their own). Safe to remove later.
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# [SUGGEST] Typo in the comment below: "fast api" should be "FastAPI".
# [EXPLAIN] Creates the single app object. Every route file attaches its routes to this same instance, and uvicorn serves it through main.py.
# [SUGGEST] Longer term, replace the shared global app with an APIRouter per resource so route files don't need to import the app at all.
#initialize the fast api app
app = FastAPI(title="Bank-App Console")

# [SUGGEST] This comment doesn't describe anything below it. Delete it, or move it next to the admin row in accounts.
# Admin object


# [EXPLAIN] Login credentials. account_type is "admin" or "user", and customer_id links a user to their row in customers below (the admin has no customer_id).
# [SUGGEST] Passwords are stored in plaintext. Fine for a throwaway demo, but real code should store only a hash (bcrypt or argon2).
# [SUGGEST] The name "accounts" is confusing in a bank app, since balances live on customers. Consider renaming to "users".
# [SUGGEST] Usernames here ("Johnathan", "Jane Doe") don't match any username in customers. Decide whether a username lives in one place or two.
accounts = [
    {"id": 1, "username": "admin", "password": "admin123", "account_type": "admin", "customer_id": None},
    {"id": 2, "username": "Johnathan", "password": "IAmJohn", "account_type": "user", "customer_id": 1},
    {"id": 3, "username": "Jane Doe", "password": "jane123", "account_type": "user", "customer_id": 2},
    {"id": 4, "username": "Rohit", "password": "rohit123", "account_type": "user", "customer_id": 3},
    {"id": 5, "username": "Mohit", "password": "mohit123", "account_type": "user", "customer_id": 4},
    {"id": 6, "username": "Shobhit", "password": "shobhit123", "account_type": "user", "customer_id": 5},

]

# [EXPLAIN] Customer profiles plus their balance. Route files import this same list object, so appending or removing in one file is visible everywhere.
# [SUGGEST] These seed rows have no "username" key, but create_customer adds one to new customers. Add username to the seed rows so every customer has the same shape.
# [SUGGEST] Balances are floats, which cause rounding errors with money (0.1 + 0.2 != 0.3). Use Decimal or integer cents.
# [SUGGEST] Never reassign this list in a route file (customers = [...]). That would break the sharing. Only append, remove, or modify in place.
customers = [
    {"id": 1, "name": "John One", "postal_code": "10001", "address": "1 Main St", "balance": 1000.0},
    {"id": 2, "name": "Jane Doe", "postal_code": "10002", "address": "2 Main St", "balance": 1500.0},
    {"id": 3, "name": "Rohit",  "postal_code": "20001", "address": "3 Park Ave", "balance": 2000.0},
    {"id": 4, "name": "Mohit",  "postal_code": "20002", "address": "4 Park Ave", "balance": 2500.0},
    {"id": 5, "name": "Shobhit",  "postal_code": "20003", "address": "5 Park Ave", "balance": 3000.0},
]

# [EXPLAIN] id_counter is the next ID to hand out. It starts at 7 because accounts 1-6 exist. Right now BOTH create_customer and create_account use it, so they share one sequence.
# [SUGGEST] Rename to account_id_counter, and have create_customer use customer_id_counter instead. Otherwise the first new customer gets ID 7 and ID 6 is skipped.
id_counter = 7
# [EXPLAIN] Intended as the next customer ID (customers 1-5 exist), but nothing uses it yet.
customer_id_counter = 6

# [EXPLAIN] Request body for POST /accounts. FastAPI validates incoming JSON against these fields.
# [SUGGEST] Missing field: route code reads account.customer_id, but it isn't defined here, so POST /accounts crashes. Add customer_id: int | None = None.
# [SUGGEST] account_type accepts any string, so a caller could create an admin account. Use Literal["admin", "user"] with a default of "user", and don't let the public endpoint create admins.
# [SUGGEST] Add a minimum length to password (Field(min_length=8)).
class AccountCreate(BaseModel):
    username: str
    password: str
    account_type: str
    customer_id: int | None = None  # Optional field to link to a customer

class AccountRead(BaseModel):
    username: str
    account_type: str




# [EXPLAIN] Request body for POST /customers, and currently also for PUT /customers/{id}.
# [SUGGEST] Add a separate CustomerUpdate model without initial_balance, since a PUT silently ignores it. Also validate initial_balance >= 0 (Field(ge=0)).
#class to create the customer
class CustomerCreate(BaseModel):
    name: str
    username: str
    postal_code: str
    address: str
    initial_balance: float = 0.0

# [EXPLAIN] Meant for deposits and withdrawals, but no route uses it yet.
# [SUGGEST] Restrict type to Literal["deposit", "withdrawal"] and require amount > 0 (Field(gt=0)). Decide who owns the future transaction route file.
#class to create transaction
class Transaction(BaseModel):
    amount: float
    type: str
