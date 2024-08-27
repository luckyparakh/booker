from fastapi import FastAPI, status
from src.books.routes import book_router
from src.auth.routers import auth_router
from src.review.routes import review_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from .errors import register_all_errors
from .middleware import register_middleware


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Start")
    await init_db()
    yield
    print("End")


version = "v1"
api_prefix = f"/api/{version}"
app = FastAPI(
    version=version,
    title="Books API",
    description="A simple API to manage books",
    # lifespan=life_span
)

register_all_errors(app)
register_middleware(app)

app.include_router(book_router, prefix=api_prefix)
app.include_router(auth_router, prefix=api_prefix)
app.include_router(review_router, prefix=api_prefix)


@app.get("/")
async def read_root():
    return {"message": "Hello World"}
