import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.db import ensure_indexes
from app.errors import AppError, app_error_handler
from app.routers import (
    attendance, auth, employees, health, holidays, locations, platform, public, reasons, shifts, users,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes()
    yield


app = FastAPI(title="Employee Tracker API", lifespan=lifespan)

app.add_exception_handler(AppError, app_error_handler)

# CORS link of the chain (spec §5.8).
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """request_id: first link of the middleware chain (spec §5.8)."""
    request.state.request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-Id"] = request.state.request_id
    return response


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(locations.router)
app.include_router(employees.router)
app.include_router(shifts.router)
app.include_router(holidays.router)
app.include_router(reasons.router)
app.include_router(public.router)
app.include_router(attendance.router)
app.include_router(platform.router)
