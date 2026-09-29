# [EXPLAIN] Delete operation for customers.
from fastapi import HTTPException
from core import app, customers

# [EXPLAIN] DELETE /customers/{customer_id} finds the customer, removes it from the shared list, and returns a message. Removing while looping is safe here only because the function returns immediately afterward.
# [SUGGEST] Deleting a customer leaves any linked account with a customer_id that points at nothing. Decide the rule: block the delete, delete the account too, or clear the link.
# [SUGGEST] Consider refusing to delete a customer whose balance is above zero.
# [SUGGEST] Same search loop as the other customer files. Use the shared helper once it exists.
@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    for existing_customer in customers:
        if existing_customer["id"] == customer_id:
            customers.remove(existing_customer)
            return {"message": "Customer deleted successfully"}
    raise HTTPException(status_code=404, detail="Customer not found")
