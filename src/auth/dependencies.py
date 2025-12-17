from typing import List

from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from src.auth.services import UserService
from src.auth.utils import decode_access_token
from src.db.main import get_session
from src.db.models import User
from src.db.redis import is_token_blocked
from src.errors import (
    AccessTokenRequiredException,
    InsufficientPermissionsException,
    InvalidTokenException,
    RefreshTokenRequiredException,
    UserNotFoundException,
)

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials if creds else None

        # If no token or invalid token, raise 403 Forbidden
        if token is None or not self.verify_token(token):
            raise InvalidTokenException()

        token_data = decode_access_token(token)

        # Check if token's JTI is in blocklist
        jti = token_data.get("jti") if token_data else None
        if jti and await is_token_blocked(jti):
            raise InvalidTokenException()

        # Additional verification based on token type
        self.verify_token_data(token_data)

        return token_data  # type: ignore

    def verify_token(self, token: str) -> bool:
        token_data = decode_access_token(token)

        return True if token_data is not None else False

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Subclasses must implement this method")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequiredException()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequiredException()


async def get_current_user(
    token_data: dict = Depends(AccessTokenBearer()), session=Depends(get_session)
):
    user_email = token_data["user"]["email"]

    if user_email is None:
        raise UserNotFoundException()

    user = await user_service.get_user_by_email(session, user_email)

    if user is None:
        raise UserNotFoundException()

    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise InsufficientPermissionsException()

        return True
