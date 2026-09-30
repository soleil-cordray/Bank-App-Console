from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    
    name: str
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8, max_length=20)
    usertype: str 
    branch_id: int = Field(..., gt=0)


class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    