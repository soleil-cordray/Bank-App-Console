# [EXPLAIN] Login and permission checks shared by the route files. Kept out of core.py so it doesn't add to merge conflicts there.
# [EXPLAIN] Add one of these to any route with Depends(...):
#   customer=Depends(customer_only)  -> logged-in customer's dict (admins get 403)
#   admin=Depends(admin_only)        -> only the admin gets through (customers get 403)
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from core import accounts, customers

# [EXPLAIN] HTTPBasic reads the username and password the caller sends. It also adds the "Authorize" button to /docs.
security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Checks username + password against core.accounts and returns the matching login."""
    for account in accounts:
        if account["username"] == credentials.username and account["password"] == credentials.password:
            return account
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )


# [EXPLAIN] The shared search loop suggested in read.py. Other route files can import it too.
def get_customer_or_404(customer_id: int):
    for customer in customers:
        if customer["id"] == customer_id:
            return customer
    raise HTTPException(status_code=404, detail="Customer not found")


def customer_only(account=Depends(get_current_user)):
    # Admins can only read, so they are blocked from every update endpoint.
    if account["account_type"] == "admin":
        raise HTTPException(status_code=403, detail="Admins cannot make updates or transactions")
    return get_customer_or_404(account["customer_id"])


def admin_only(account=Depends(get_current_user)):
    if account["account_type"] != "admin":
        raise HTTPException(status_code=403, detail="Only an admin can do this")
    return account
