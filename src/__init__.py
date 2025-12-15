import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.reviews.routes import review_router
from src.db.main import init_db
from src.errors import (create_exception_handler,InvalidCredentialsException, InsufficientPermissionsException,
                    BookNotFoundException, UserNotFoundException,InvalidTokenException)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("✅ Server has started...")
    await init_db()
    yield
    logger.info("🏁 Server has stopped!")


version = "v1"

app = FastAPI(
    title="Bookly",
    version=version,
    port=8000,
    description="Book collection application",
    # lifespan=lifespan,
)

app.add_exception_handler(
    InvalidCredentialsException,
    create_exception_handler(status_code=status.HTTP_401_UNAUTHORIZED, initial_details={"message": "Invalid email or password","error_code": "INVALID_CREDENTIALS"}),
)

app.add_exception_handler(
    InvalidTokenException,
    create_exception_handler(status_code=status.HTTP_401_UNAUTHORIZED, initial_details={"message": "Token is invalid or expired.","error_code": "INVALID_TOKEN"}),
)

app.add_exception_handler(
    UserNotFoundException,
    create_exception_handler(status_code=status.HTTP_404_NOT_FOUND, initial_details={"message": "User not found","error_code": "USER_NOT_FOUND"}),
)

app.add_exception_handler(
    BookNotFoundException,
    create_exception_handler(status_code=status.HTTP_404_NOT_FOUND, initial_details={"message": "Book not found","error_code": "BOOK_NOT_FOUND"}),
)

app.add_exception_handler(
    InsufficientPermissionsException,
    create_exception_handler(status_code=status.HTTP_403_FORBIDDEN, initial_details={"message": "You do not have permission to perform this action","error_code": "INSUFFICIENT_PERMISSIONS"}),
)

 
@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    logger.error(f"🚨 Internal server error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An internal server error occurred.","error_code": "INTERNAL_SERVER_ERROR"},
    )



@app.get("/")
async def health():
    return {"message": "Welcome to bookly"}

  
app.include_router(router=book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(router=auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(
    router=review_router, prefix=f"/api/{version}/reviews", tags=["reviews"]
)
