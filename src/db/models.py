# Books Model
import uuid
from datetime import datetime
from typing import Optional,List

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel

class Book(SQLModel, table=True):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=256)
    author: str
    publisher: str
    publish_date: str
    page_count: int
    language: str
    user_id: Optional[uuid.UUID] = Field(default=None,foreign_key="user.uid")
    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP)
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP)
    )
    
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(back_populates="book",sa_relationship_kwargs={"lazy":"selectin"})


    def __repr__(self):
        return f"<Book {self.title}>"


# User Model
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
    reviews: List["Review"] = Relationship(back_populates="user",sa_relationship_kwargs={"lazy":"selectin"})

    def __repr__(self):
        return f"<User {self.username}>"


# Review Model
class Review(SQLModel, table=True):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    book_id: uuid.UUID = Field(foreign_key="book.uid")
    user_id: uuid.UUID = Field(foreign_key="user.uid")
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    book: Optional["Book"] = Relationship(back_populates="reviews")
    user: Optional["User"] = Relationship(back_populates="reviews")


    def __repr__(self):
        return f"<Review {self.uid} - Book {self.book_id} by User {self.user_id}>"  