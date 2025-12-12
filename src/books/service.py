from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import desc, select

from src.books.models import Book
from src.books.schemas import BookCreateModel, BookUpdateModel


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.execute(statement)

        return result.scalars().all()

    async def get_book(self, session: AsyncSession, book_id: str):
        statement = select(Book).where(Book.uid == book_id)
        result = await session.execute(statement)
        book = result.scalar_one_or_none()

        return book

    async def create_book(self, session: AsyncSession, book_data: BookCreateModel):
        new_book = Book.model_validate(book_data)
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)

        return new_book

    async def update_book(
        self, session: AsyncSession, book_id, updated_book: BookUpdateModel
    ):
        book_to_update = await self.get_book(session, book_id)

        if book_to_update is not None:
            for key, value in updated_book.model_dump().items():
                setattr(book_to_update, key, value)

            # session.add(book_to_update)
            await session.commit()
            await session.refresh(book_to_update)
            return book_to_update

        return None

    async def delete_book(self, session: AsyncSession, book_id):
        book_to_delete = await self.get_book(session, book_id)

        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()

        else:
            return None
