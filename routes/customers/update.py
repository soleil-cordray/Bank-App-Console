# [EXPLAIN] Update operation for customers.
from fastapi import HTTPException
from core import app, customers, CustomerCreate

# [EXPLAIN] PUT /customers/{customer_id} finds the customer and overwrites name, username, postal_code, and address. It never touches id or balance, which is why initial_balance in the body is ignored.
# [SUGGEST] Use a dedicated CustomerUpdate model (no initial_balance) so the API doesn't accept a field it ignores.
# [SUGGEST] Check that the new username isn't already used by a different customer.
# [SUGGEST] PUT means "replace everything", which fits since all four fields are required. If you later want partial edits, add a PATCH route.
# [SUGGEST] Same search loop as read.py and delete.py. Use the shared helper once it exists.
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
