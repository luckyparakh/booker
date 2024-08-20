from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db 


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Start")
    await init_db()
    yield
    print("End")


version = "v1"
app = FastAPI(
    version=version,
    title="Books API",
    description="A simple API to manage books",
    lifespan=life_span
)

app.include_router(book_router, prefix=f"/api/{version}")


@app.get("/")
async def read_root():
    return {"message": "Hello World"}
