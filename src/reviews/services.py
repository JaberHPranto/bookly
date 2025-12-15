from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from src.reviews.schemas import ReviewCreateModel
from src.db.models import Review
from src.books.service import BookService

import uuid


book_service = BookService()

class ReviewService:
    async def add_review(self,session:AsyncSession, user_id: uuid.UUID, book_id: str,review_data: ReviewCreateModel):
        try:
            book = await book_service.get_book(session, book_id)
            if not book:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
            
            new_review_payload = {
                "book_id": book_id,
                "user_id": user_id,
                "rating": review_data.rating,
                "comment": review_data.comment
            }

            new_review = Review(**new_review_payload)
            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)

            return new_review
        
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while adding the review.")