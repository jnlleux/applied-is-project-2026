from pathlib import Path
from fastapi.staticfiles import StaticFiles
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

app.mount("/showroom", StaticFiles(directory=Path(__file__).parent / "static/showroom", html=True), name="showroom")

from fastapi import Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.security import require_user

@app.get('/auth/me')
def me(user=Depends(require_user)):
    return user

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    errors = [{'loc': list(e['loc']), 'type': e['type'], 'msg': e['msg']} for e in exc.errors()]
    status = 400 if any(e['type'] == 'json_invalid' for e in exc.errors()) else 422
    return JSONResponse(status_code=status, content={'detail': errors})
