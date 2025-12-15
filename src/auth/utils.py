import uuid
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi.exceptions import HTTPException
from passlib.context import CryptContext
from starlette import status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_data: dict, expiry: Optional[timedelta] = None, refresh: bool = False
) -> str:
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now() + (expiry if expiry else timedelta(minutes=30))
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(payload=payload, key="VERY_SECRET_KEY", algorithm="HS256")
    return token


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(jwt=token, key="VERY_SECRET_KEY", algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Token decode error: {str(e)}"
        )
