from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import medicines   # NEW

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(title="Medicine Inventory & Order API", lifespan=lifespan)

app.include_router(medicines.router)   # NEW

@app.get("/")
def root():
    return {"status": "ok"}