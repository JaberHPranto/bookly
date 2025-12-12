from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from src.auth.dependencies import AccessTokenBearer
from src.books.schemas import Book, BookCreateModel, BookUpdateModel
from src.books.service import BookService
from src.db.main import get_session

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()


@book_router.get(
    "/",
    response_model=List[Book],
    status_code=status.HTTP_200_OK,
)
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    user_details: str = Depends(access_token_bearer),
):
    books = await book_service.get_all_books(session)
    return books


@book_router.get(
    "/{book_id}",
    status_code=status.HTTP_200_OK,
    response_model=Book,
)
async def get_book(
    book_id: str,
    session: AsyncSession = Depends(get_session),
    user_details: str = Depends(access_token_bearer),
):
    book = await book_service.get_book(session, book_id)
    if book:
        return book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@book_router.post(
    "/",
    response_model=Book,
    status_code=status.HTTP_201_CREATED,
)
async def create_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    user_details: str = Depends(access_token_bearer),
) -> dict:
    new_book = await book_service.create_book(session, book_data)

    return {"message": "Book created successfully", "data": new_book}


@book_router.patch("/{book_id}", response_model=Book, status_code=status.HTTP_200_OK)
async def update_book(
    book_id: str,
    updated_book_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    user_details: str = Depends(access_token_bearer),
):
    updated_book = await book_service.update_book(session, book_id, updated_book_data)
    if updated_book:
        return {"message": "Book updated successfully", "data": updated_book}

    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Book not found !")


@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    session: AsyncSession = Depends(get_session),
    user_details: str = Depends(access_token_bearer),
):
    deleted_book = await book_service.delete_book(session, book_id)
    if deleted_book is None:
        return {"message": "Book deleted successfully"}

    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Book not found !")
