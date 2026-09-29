from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


#initialize the fat api app
app = FastAPI(title="Bank-App Console")

# Admin object
ADMIN = {"username": "admin", "password": "admin123"}

customers = [
    {"id": 1, "name": "John One", "username": "john1", "postal_code": "10001", "address": "1 Main St", "balance": 1000.0},
    {"id": 2, "name": "John Two", "username": "john2", "postal_code": "10002", "address": "2 Main St", "balance": 1500.0},
    {"id": 3, "name": "Rohit", "username": "rohit", "postal_code": "20001", "address": "3 Park Ave", "balance": 2000.0},
    {"id": 4, "name": "Mohit", "username": "mohit", "postal_code": "20002", "address": "4 Park Ave", "balance": 2500.0},
    {"id": 5, "name": "Shobhit", "username": "shobhit", "postal_code": "20003", "address": "5 Park Ave", "balance": 3000.0},
]

id_counter = 6

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