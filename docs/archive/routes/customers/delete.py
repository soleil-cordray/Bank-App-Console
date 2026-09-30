
from fastapi import Depends

from auth import admin_only, get_customer_or_404
from core import accounts, app, customers



@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, admin=Depends(admin_only)):
    customer = get_customer_or_404(customer_id)
    customers.remove(customer)
    
    accounts[:] = [account for account in accounts if account.get("customer_id") != customer_id]
    
    return {"message": "Customer deleted successfully", "customer": customer}
