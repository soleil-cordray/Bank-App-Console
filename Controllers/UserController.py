from fastapi import HTTPException
from core import app
from Models.User import UserResponse, UserCreate

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):
    # Implementation for creating a new user
    pass

@app.get("/users/", response_model=list[UserResponse])
def read_users():
    # Implementation for reading all users
    pass

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int):
    # Implementation for reading a specific user by ID
    pass

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate):
    # Implementation for updating a specific user by ID
    pass

@app.delete("/users/{user_id}", response_model=UserResponse)
def delete_user(user_id: int):      
    # Implementation for deleting a specific user by ID
    pass

