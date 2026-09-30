# app/models/branch.py
# CHANGED (was Models/Branch.py, which only had name + location)
# REFS: 1.1 (Branch fields), 1.3 + 3.3 (the staff data both ratios need)

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

# -----------------------------------------------------------------------------
# STAFF [1.3, 3.3]
# -----------------------------------------------------------------------------

class StaffMember(BaseModel):
    '''One entry of a branch's staff_list.'''
    # RATIO QUESTIONS: "staff-to-manager" [1.3], "non-direct/contract" [3.3]
    # - who each person is (staff_id, so manager_id can point at them)
    # - whether they are direct/contract staff (employment_type)
    staff_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1)
    employment_type: Literal["DIRECT", "CONTRACT"]


def validate_staff(staff_list, manager_id):
    '''Rules that tie manager_id to staff_list. Raises ValueError.'''
    ids = [member.staff_id if isinstance(member, StaffMember) else member["staff_id"] for member in staff_list]
    if len(ids) != len(set(ids)):
        raise ValueError("staff_id values must be unique inside a branch")
    if manager_id is not None and manager_id not in ids:
        raise ValueError("manager_id must be the staff_id of someone in staff_list")

# -----------------------------------------------------------------------------
# BRANCH [1.1, 3.3]
# -----------------------------------------------------------------------------

class BranchCreate(BaseModel):
    '''Body of POST /api/v1/branches.'''
    branch_code: str = Field(..., min_length=1)
    location: str = Field(..., min_length=3, max_length=100)
    manager_id: int | None = None # the staff_id of the branch manager
    staff_list: list[StaffMember] = []

    # EMBEDDEDING [3.C]: staff are EMBEDDED in their branch's document
    # - only ever read together with the branch
    # REFERENCING [3.C]: accounts & transactiion REFERENCE each other
    # - by owner_id, account_number, branch_id
    # - because they grow without limit & are queried on their own
    @model_validator(mode="after")
    def _manager_works_here(self):
        validate_staff(self.staff_list, self.manager_id)
        return self


class BranchUpdate(BaseModel):
    '''Body of PUT /api/v1/branches/{branch_id}; send only what changes.'''
    branch_code: str | None = Field(None, min_length=1)
    location: str | None = Field(None, min_length=3, max_length=100)
    manager_id: int | None = None
    staff_list: list[StaffMember] | None = None


class Branch(BaseModel):
    '''The Branch model & what the API returns.'''
    branch_id: int
    branch_code: str
    location: str
    manager_id: int | None
    staff_list: list[StaffMember]
    created_at: datetime # NEW
    is_active: bool
