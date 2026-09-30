# app/models/customer.py
# CHANGED (was Models/User.py, renamed to customer for class-tie)
# REFS: 1.1 (Customer fields), 2.2 (customer endpoint bodies)

from datetime import datetime

from pydantic import BaseModel, Field

EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
USERNAME_PATTERN = r"^[a-zA-Z0-9_]+$" # letters, numbers, underscores

# [1.1]
class CustomerCreate(BaseModel):
    '''Body of POST /api/v1/customers (sign up: customer profile + login).'''
    name: str = Field(..., min_length=1) # blank names rejected
    email: str = Field(..., pattern=EMAIL_PATTERN)
    branch_id: int = Field(..., gt=0)
    # LOGIN: basic username + password (stored as-is for now; hashing comes later)
    username: str = Field(..., min_length=3, max_length=20, pattern=USERNAME_PATTERN)
    password: str = Field(..., min_length=8, max_length=64)


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
    # NEVER includes the password
    customer_id: int # WAS user_id
    username: str
    name: str
    email: str
    accounts_list: list[str] = [] # customer's account numbers
    branch_id: int
    created_at: datetime # the indexed field [3.1]
    is_active: bool # DELETE deactivates instead of removing [2.2]
    close_requested: bool = False # customer asked the admin to close their profile
