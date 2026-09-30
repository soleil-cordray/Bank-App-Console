from pydantic import BaseModel, ConfigDict, Field

class TransactionBase(BaseModel):

    amount: float = Field(..., gt=0)
    account_id_to: int  | None
    account_id_from: int | None
    timestamp: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')  # ISO 8601 format



class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: int