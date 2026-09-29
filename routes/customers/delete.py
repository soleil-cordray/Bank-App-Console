# [EXPLAIN] Delete operation for customers. Only the admin can delete. Customers have to ask the admin.
from fastapi import Depends

from auth import admin_only, get_customer_or_404
from core import accounts, app, customers


# [EXPLAIN] DELETE /customers/{customer_id} removes the customer and their login, so no account is left pointing at a customer that no longer exists.
@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, admin=Depends(admin_only)):
    customer = get_customer_or_404(customer_id)
    customers.remove(customer)
    # [:] changes the shared list in place instead of making a new one (see the note on customers in core.py).
    accounts[:] = [account for account in accounts if account.get("customer_id") != customer_id]
    # Their transactions stay in the log: banks keep records after closing an account.
    return {"message": "Customer deleted successfully", "customer": customer}
