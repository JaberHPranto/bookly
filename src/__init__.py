import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.db.main import init_db

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


@app.get("/")
async def health():
    return {"message": "Welcome to bookly"}


app.include_router(router=book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(router=auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
