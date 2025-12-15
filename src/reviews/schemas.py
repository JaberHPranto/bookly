from pydantic import BaseModel
import uuid
from typing import Optional
from datetime import datetime

class ReviewModel(BaseModel):
    uid: uuid.UUID
    user_id: Optional[uuid.UUID]
    book_id: Optional[uuid.UUID]
    rating: int
    comment: Optional[str] = None
    updated_at: datetime
    created_at: datetime

class ReviewCreateModel(BaseModel):
    rating: int
    comment: Optional[str] = None
