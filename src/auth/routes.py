from datetime import datetime, timedelta

from fastapi import APIRouter, Body, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.auth.dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_user,
)
from src.auth.schemas import (
    EmailSchema,
    UserCreateModel,
    UserLoginModel,
    UserModelWithBooks,
)
from src.auth.services import UserService
from src.auth.utils import (
    create_access_token,
    create_email_confirmation_token,
    hash_password,
    verify_email_confirmation_token,
    verify_password,
)
from src.celery_tasks import send_email
from src.config import Config
from src.db.main import get_session
from src.db.redis import add_token_to_blocklist
from src.errors import InvalidCredentialsException, UserNotFoundException
from src.mail import create_message, mail

auth_router = APIRouter()
user_service = UserService()
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])


@auth_router.post("/send-mail")
async def send_test_mail(recipients: EmailSchema):
    send_email.delay(  # type: ignore[attr-defined]
        recipients=recipients.email_addresses,
        subject="Test Mail from Bookly",
        body="<h1>This is a test email from Bookly application.</h1>",
    )

    return {"message": "Mail sent successfully"}


@auth_router.get("/verify-email")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    decoded_email = verify_email_confirmation_token(token)

    if not decoded_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user = await user_service.get_user_by_email(session, decoded_email)

    if not user:
        raise UserNotFoundException()

    await user_service.update_users(session, user, {"is_verified": True})

    return {"message": "Email verified successfully"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
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

    # User verification
    verification_token = create_email_confirmation_token(new_user.email)
    verification_link = (
        f"{Config.DOMAIN}/api/v1/auth/verify-email?token={verification_token}"
    )

    email_template = f"""
    <html>
        <body>
            <h2>Welcome to Bookly, {new_user.first_name} {new_user.last_name}!</h2>
            <p>Thank you for signing up. Please verify your email address by clicking the link below:</p>
            <a href="{verification_link}">Verify Email</a>
            <p>If you did not sign up for this account, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The Bookly Team</p>
        </body>
    </html>
    """

    message = create_message(
        subject="Welcome to Bookly - Verify Your Email",
        recipients=[new_user.email],
        body=email_template,
    )

    email_sent = True
    try:
        await mail.send_message(message)
    except Exception as e:
        # Log the error but don't fail the signup
        print(f"Failed to send verification email: {e}")
        email_sent = False

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "User created successfully. Please check your email to verify your account."
            if email_sent
            else "User created successfully. Email verification is temporarily unavailable.",
            "user": new_user.model_dump(mode="json"),
        },
    )


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
                "role": user.role,
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
            raise InvalidCredentialsException()

    else:
        raise InvalidCredentialsException()


@auth_router.get("/refresh-token")
async def get_new_access_token(token_details: dict = Depends(refresh_token_bearer)):
    user_data = token_details["user"]
    token_expiry = token_details["exp"]

    if (datetime.fromtimestamp(token_expiry) - datetime.now()).days < 0:
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


@auth_router.get("/me", response_model=UserModelWithBooks)
async def get_current_user_details(
    current_user: UserModelWithBooks = Depends(get_current_user),
    _: bool = Depends(role_checker),
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


@auth_router.post("/reset-password-request")
async def password_reset_request(
    email: str = Body(..., embed=True), session: AsyncSession = Depends(get_session)
):
    user = await user_service.get_user_by_email(session, email)
    if not user:
        raise UserNotFoundException()

    verification_token = create_email_confirmation_token(user.email)
    reset_link = (
        f"{Config.DOMAIN}/api/v1/auth/reset-password?token={verification_token}"
    )

    reset_password_template = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hi {user.first_name},</p>
            <p>We received a request to reset your password. Click the link below to reset your password:</p>
            <a href="{reset_link}">Reset Password</a>
            <p>If you did not request a password reset, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The Bookly Team</p>
        </body>
    </html>
    """

    message = create_message(
        subject="Bookly - Password Reset Request",
        recipients=[user.email],
        body=reset_password_template,
    )

    await mail.send_message(message)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Password reset link has been sent to your email."},
    )


@auth_router.post("/reset-password")
async def reset_password(
    token: str,
    password: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    decoded_email = verify_email_confirmation_token(token)

    if not decoded_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    user = await user_service.get_user_by_email(session, decoded_email)

    if not user:
        raise UserNotFoundException()

    hashed_password = hash_password(password)
    await user_service.update_users(session, user, {"hashed_password": hashed_password})

    return {"message": "Password has been reset successfully"}
