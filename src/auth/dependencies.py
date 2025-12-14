from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from starlette import status

from src.auth.utils import decode_access_token
from src.db.redis import is_token_blocked


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials if creds else None

        # If no token or invalid token, raise 403 Forbidden
        if token is None or not self.verify_token(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail={
                    "message": "Token is invalid or expired.",
                    "resolution": "Please log in again to obtain a new token"
                }
            )

        token_data = decode_access_token(token)
        
        # Check if token's JTI is in blocklist
        jti = token_data.get("jti") if token_data else None
        if jti and await is_token_blocked(jti):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail={
                    "message": "Token has been revoked",
                    "resolution": "Please log in again to obtain a new token"
                }
            )

        # Additional verification based on token type
        self.verify_token_data(token_data)
     
        return token_data  # type: ignore

    def verify_token(self, token: str) -> bool:
        token_data = decode_access_token(token)

        return True if token_data is not None else False
    
    def verify_token_data(self, token_data:dict) -> None:
        raise NotImplementedError("Subclasses must implement this method")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token",
            )
        
 
class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token",
            )    