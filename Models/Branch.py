from pydantic import BaseModel, ConfigDict, Field

class BranchBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    location: str = Field(..., min_length=3, max_length=100)

class BranchCreate(BranchBase):
    pass

class BranchResponse(BranchBase):
    model_config = ConfigDict(from_attributes=True)

    branch_id: int

    