# app/models/customer.py
# CHANGED (was Models/User.py, renamed to customer for class-tie)
# REFS: 1.1 (Customer fields), 2.2 (customer endpoint bodies)

from pydantic import BaseModel, ConfigDict, Field

EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# [1.1]
class CustomerCreate(BaseModel):
    '''Body of POST /api/v1/customers (create customer profile).'''
    name: str = Field(..., min_length=1) # blank names rejected
    email: str = Field(..., pattern=EMAIL_PATTERN)
    branch_id: int = Field(..., gt=0)
    # REMOVED username, password, usertype
    # - Customer: ID, Name, Email, Accounts list, Branch ID
    # - removing `password`: can't be stored/returned in plaintext (safer)


# [2.2]
class CustomerUpdate(BaseModel):
    '''Body of PUT /api/v1/customers/{id} (update info).'''
    # every field is optional (sends only what changes)
    name: str | None = Field(None, min_length=1)
    email: str | None = Field(None, pattern=EMAIL_PATTERN)
    branch_id: int | None = Field(None, gt=0)


# [1.1]
class Customer(BaseModel):
    '''The Customer model & what the API returns.'''
    customer_id: int # WAS user_id
    name: str
    email: str
    accounts_list: list[str] = [] # customer's account numbers
    branch_id: int
    created_at: datetime # the indexed field [3.1]
    is_active: bool # DELETE deactivates instead of removing [2.2]
