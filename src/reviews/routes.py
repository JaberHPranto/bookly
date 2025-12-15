
from fastapi import APIRouter, Depends
from src.db.main import get_session
from src.db.models import User
from src.reviews.services import ReviewService
from src.auth.dependencies import AccessTokenBearer, RoleChecker, get_current_user
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.reviews.schemas import ReviewCreateModel

review_router = APIRouter()
router_service = ReviewService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin","user"]))


@review_router.post("/book/{book_id}")
async def create_review(
        book_id:str,
        review_data:ReviewCreateModel,
        session: AsyncSession = Depends(get_session),
        user_details: User = Depends(get_current_user)):
    
    user_id = user_details.uid
    review = await router_service.add_review(session,user_id=user_id,book_id=book_id,review_data=review_data) 

    return review