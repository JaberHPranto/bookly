from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer, RoleChecker, get_current_user
from src.auth.schemas import UserCreateModel, UserLoginModel, UserModel, UserModelWithBooks
from src.auth.services import UserService
from src.auth.utils import create_access_token, verify_password
from src.db.redis import add_token_to_blocklist
from src.db.main import get_session

auth_router = APIRouter()
user_service = UserService()
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin","user"])

@auth_router.post(
    "/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED
)
async def signup(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    is_user_exist = await user_service.is_user_exist(session, user_data.email)
    if is_user_exist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with this email already exists",
        ) 

    new_user = await user_service.create_user(session, user_data)
    return new_user


@auth_router.post("/login")
async def login(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    user = await user_service.get_user_by_email(session, login_data.email)

    if user is not None:
        is_valid_password = verify_password(login_data.password, user.hashed_password)

        if is_valid_password:
            user_payload = {
                "uid": str(user.uid),
                "email": user.email,
                "role":user.role
            }
            access_token = create_access_token(user_payload)
            refresh_token = create_access_token(
                user_payload, expiry=timedelta(days=2), refresh=True
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )


@auth_router.get("/refresh-token")
async def get_new_access_token(token_details: dict = Depends(refresh_token_bearer)):
    user_data = token_details["user"]
    token_expiry = token_details["exp"]

    if(datetime.fromtimestamp(token_expiry) - datetime.now()).days < 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Refresh token has expired, please login again",
        )

    new_access_token = create_access_token(user_data)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Access token refreshed successfully",
            "access_token": new_access_token,
        },
    )

@auth_router.get("/me",response_model=UserModelWithBooks)
async def get_current_user_details(
    current_user: UserModelWithBooks = Depends(get_current_user),
    _: bool = Depends(role_checker)
):
    return current_user

@auth_router.post("/logout")
async def revoke_token(
    token_details: dict = Depends(access_token_bearer),
):
    jti = token_details["jti"]

    await add_token_to_blocklist(jti)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Logout successful"},
    )
