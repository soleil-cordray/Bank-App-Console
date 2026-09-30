
import core
from core import app, customers, CustomerCreate


#create a customer
@app.post("/customers")
def create_customer(customer: CustomerCreate):
    

    new_customer = {
        
        "id": core.customer_id_counter,
        "name": customer.name,
        "postal_code": customer.postal_code,
        "address": customer.address,
        "balance": customer.initial_balance
    }

    customers.append(new_customer)
    
    core.customer_id_counter += 1

    return new_customer
