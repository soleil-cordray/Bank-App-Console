# [EXPLAIN] `import core` (not just `from core import ...`) is needed because this file changes core.id_counter. A `from` import would copy the number and the increment would never reach the real counter.
import core
from core import app, customers, CustomerCreate

# [EXPLAIN] POST /customers builds a new customer dict from the request body, appends it to the shared list, bumps the counter, and returns the new customer.
# [SUGGEST] Use customer_id_counter here, not id_counter (see the note in core.py).
# [SUGGEST] There's no check for a duplicate username. Add one.
# [SUGGEST] Return status code 201 for a successful create: @app.post("/customers", status_code=201).
# [SUGGEST] Wrap "take the next ID and increment" in a small next_id() helper so route files never touch the counter directly.
#create a customer
@app.post("/customers")
def create_customer(customer: CustomerCreate):
    # global id_counter   (original; replaced by core.id_counter below so the counter is shared across files)

    new_customer = {
        # "id": id_counter,   (original)
        "id": core.customer_id_counter,
        "name": customer.name,
        "postal_code": customer.postal_code,
        "address": customer.address,
        "balance": customer.initial_balance
    }

    customers.append(new_customer)
    # id_counter += 1   (original)
    core.id_counter += 1

    return new_customer
