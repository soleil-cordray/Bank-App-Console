
from fastapi import HTTPException
from core import CustomerRead, app, customers

@app.get("/customers", response_model=list[CustomerRead])
def get_customers(
    min_balance: float | None = None,
    max_balance: float | None = None
):
    filtered_customers = customers
    if min_balance is not None:
        filtered_customers = [customer for customer in filtered_customers if customer["balance"] >= min_balance]
    if max_balance is not None:
        filtered_customers = [customer for customer in filtered_customers if customer["balance"] <= max_balance]
    return filtered_customers


@app.get("/customers/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int):
    for customer in customers:
        if customer["id"] == customer_id:
            return customer
    raise HTTPException(status_code=404, detail="Customer not found")
