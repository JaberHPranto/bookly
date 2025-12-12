import uuid
from datetime import datetime

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, SQLModel


class Book(SQLModel, table=True):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=256)
    author: str
    publisher: str
    publish_date: str
    page_count: int
    language: str
    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP)
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP)
    )


def __repr__(self):
    return f"<Book {self.title}>"
