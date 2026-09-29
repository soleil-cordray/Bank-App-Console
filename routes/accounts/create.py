# [EXPLAIN] Create operation for accounts (login credentials). As in customers/create.py, `import core` is needed so the shared counter is updated for real.
import core
from core import app, accounts, AccountCreate

# [EXPLAIN] POST /accounts builds an account dict from the request body, appends it to the shared list, bumps the counter, and returns it.
# [SUGGEST] Currently crashes: AccountCreate has no customer_id field, so account.customer_id raises AttributeError. Fix in core.py first.
# [SUGGEST] Check that the username isn't already taken, and that customer_id (if given) points to a real customer.
# [SUGGEST] The response includes the plaintext password. Hash it before storing, and return a response model that leaves it out.
# [SUGGEST] Don't let callers choose account_type freely. Anyone could create an admin.
# [SUGGEST] Use a dedicated account counter (see core.py) and return status 201.
@app.post("/accounts")
def create_account(account: AccountCreate):
    # global id_counter   (original; replaced by core.id_counter below so the counter is shared across files)

    new_account = {
        # "id": id_counter,   (original)
        "id": core.id_counter,
        "username": account.username,
        "password": account.password,
        "account_type": account.account_type,
        "customer_id": account.customer_id,
    }

    accounts.append(new_account)
    # id_counter += 1   (original)
    core.id_counter += 1

    return new_account
