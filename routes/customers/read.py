# [EXPLAIN] Read operations for customers: list all and fetch one. Importing `app` and `customers` from core means these decorators register on the same app the rest of the project uses.
from fastapi import HTTPException
from core import CustomerRead, app, customers

# [EXPLAIN] GET /customers returns the entire customers list.
# [SUGGEST] Fine for a demo. Later, add pagination and restrict this to admins.
#getter for customer
@app.get("/customers", response_model=list[CustomerRead])
def get_customers():
    return customers

# [EXPLAIN] GET /customers/{customer_id} scans the list for a matching id and returns it, or a 404.
# [SUGGEST] This same search loop is copy-pasted in update.py and delete.py. Put it in one helper (e.g. get_customer_or_404 in core.py) and reuse it. Storing customers in a dict keyed by id would remove the loop entirely.
@app.get("/customers/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int):
    for customer in customers:
        if customer["id"] == customer_id:
            return customer
    raise HTTPException(status_code=404, detail="Customer not found")
