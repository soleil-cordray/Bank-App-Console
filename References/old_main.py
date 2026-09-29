from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


#initialize the fat api app
app = FastAPI(title="Bank-App Console")

# Admin object


accounts = [
    {"id": 1, "username": "admin", "password": "admin123", "account_type": "admin"},
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

id_counter = 7
customer_id_counter = 6

class AccountCreate(BaseModel):
    username: str
    password: str
    account_type: str

    


#class to create the customer
class CustomerCreate(BaseModel):
    name: str
    username: str
    postal_code: str
    address: str
    initial_balance: float = 0.0

#class to create transaction
class Transaction(BaseModel):
    amount: float
    type: str 

#getter for customer
@app.get("/customers")
def get_customers():
    return customers

#create a customer
@app.post("/customers")
def create_customer(customer: CustomerCreate):
    global id_counter

    new_customer = {
        "id": id_counter,
        "name": customer.name,
        "username": customer.username,
        "postal_code": customer.postal_code,
        "address": customer.address,
        "balance": customer.initial_balance
    }

    customers.append(new_customer)
    id_counter += 1

    return new_customer

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    for customer in customers:
        if customer["id"] == customer_id:
            return customer
    raise HTTPException(status_code=404, detail="Customer not found")

@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer: CustomerCreate):
    for existing_customer in customers:
        if existing_customer["id"] == customer_id:
            existing_customer["name"] = customer.name
            existing_customer["username"] = customer.username
            existing_customer["postal_code"] = customer.postal_code
            existing_customer["address"] = customer.address
            return existing_customer
    raise HTTPException(status_code=404, detail="Customer not found")

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    for existing_customer in customers:
        if existing_customer["id"] == customer_id:
            customers.remove(existing_customer)
            return {"message": "Customer deleted successfully"}
    raise HTTPException(status_code=404, detail="Customer not found")

@app.post("/accounts")
def create_account(account: AccountCreate):
    global id_counter

    new_account = {
        "id": id_counter,
        "username": account.username,
        "password": account.password,
        "account_type": account.account_type,
        "customer_id": account.customer_id,
    }

    accounts.append(new_account)
    id_counter += 1

    return new_account