import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    email: str
    username: str
    first_name: str
    last_name: str
    hashed_password: str = Field(exclude=True, default_factory=lambda: "")
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


def __repr__(self):
    return f"<User {self.username}>"
