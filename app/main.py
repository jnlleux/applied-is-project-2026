from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.db import init_db
from app.routers.items import router

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(title="AutoRent", version="1.0.0", lifespan=lifespan)
app.include_router(router)

@app.get("/")
def root():
    return {"status": "ok", "project": "AutoRent"}
