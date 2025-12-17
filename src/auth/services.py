from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.auth.schemas import UserCreateModel
from src.auth.utils import hash_password
from src.db.models import User


class UserService:
    async def get_user_by_email(self, session: AsyncSession, email: str):
        statment = select(User).where(User.email == email)
        result = await session.execute(statment)

        return result.scalar_one_or_none()

    async def is_user_exist(self, session: AsyncSession, email: str) -> bool:
        user = await self.get_user_by_email(session, email)
        return True if user else False

    async def create_user(self, session: AsyncSession, user_data: UserCreateModel):
        new_user = User.model_validate(user_data)
        new_user.hashed_password = hash_password(user_data.password)
        new_user.role = "user"

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user

    async def update_users(self, session: AsyncSession, user: User, update_data: dict):
        for key, value in update_data.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)

        return user
