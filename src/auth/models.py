import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

# Avoid circular import issues
if TYPE_CHECKING:
    from src.books.models import Book


class User(SQLModel, table=True):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    email: str
    username: str
    first_name: str
    last_name: str
    hashed_password: str = Field(exclude=True, default="")
    is_verified: bool = False
    role: str = Field(default="user", nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    books: List["Book"] = Relationship(back_populates="user",sa_relationship_kwargs={"lazy":"selectin"}) 


def __repr__(self):
    return f"<User {self.username}>"
