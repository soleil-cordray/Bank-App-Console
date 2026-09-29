from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="Bank-App Console")


accounts = [
    {"id": 1, "username": "admin", "password": "admin123", "account_type": "admin", "customer_id": None},
    {"id": 2, "username": "Johnathan", "password": "IAmJohn", "account_type": "user", "customer_id": 1},
    {"id": 3, "username": "Jane Doe", "password": "jane123", "account_type": "user", "customer_id": 2},
    {"id": 4, "username": "Rohit", "password": "rohit123", "account_type": "user", "customer_id": 3},
    {"id": 5, "username": "Mohit", "password": "mohit123", "account_type": "user", "customer_id": 4},
    {"id": 6, "username": "Shobhit", "password": "shobhit123", "account_type": "user", "customer_id": 5},

]

customers = [
    {"id": 1, "name": "John One", "postal_code": "10001", "address": "1 Main St", "balance": 1000.0},
    {"id": 2, "name": "Jane Doe", "postal_code": "10002", "address": "2 Main St", "balance": 1500.0},
    {"id": 3, "name": "Rohit",  "postal_code": "20001", "address": "3 Park Ave", "balance": 2000.0},
    {"id": 4, "name": "Mohit",  "postal_code": "20002", "address": "4 Park Ave", "balance": 2500.0},
    {"id": 5, "name": "Shobhit",  "postal_code": "20003", "address": "5 Park Ave", "balance": 3000.0},
]

account_id_counter = 7

customer_id_counter = 6

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
    postal_code: str
    address: str
    initial_balance: float = 0.0

class CustomerRead(BaseModel):
    name: str
    postal_code: str
    address: str
    balance: float

# [EXPLAIN] Meant for deposits and withdrawals, but no route uses it yet.
# [SUGGEST] Restrict type to Literal["deposit", "withdrawal"] and require amount > 0 (Field(gt=0)). Decide who owns the future transaction route file.
#class to create transaction
class Transaction(BaseModel):
    amount: float
    type: str
