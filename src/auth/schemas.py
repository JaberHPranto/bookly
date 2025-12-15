import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from src.books.schemas import Book


class UserCreateModel(BaseModel):
    username: str = Field(..., max_length=50)
    first_name: str = Field(..., max_length=25)
    last_name: str = Field(..., max_length=25)
    email: str = Field(..., max_length=100)
    password: str = Field(
        ..., min_length=6, description="Password must be at least 6 characters long"
    )


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

class UserModelWithBooks(UserModel):
    books: List[Book] = []

class UserLoginModel(BaseModel):
    email: str
    password: str
