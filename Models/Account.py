from pydantic import BaseModel, ConfigDict, Field

class AccountBase(BaseModel):
    account_number: str = Field(..., min_length=10, max_length=20)
    account_type: str
    balance: float = Field(..., ge=0)
    user_id: int = Field(..., gt=0)


class AccountCreate(AccountBase):
    pass


class AccountResponse(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    account_id: int