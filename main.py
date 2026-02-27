from fastapi import FastAPI, APIRouter, Depends
from app.db import SessionLocal,  get_db
from app.routes import auth, employee
from sqlalchemy import select, text
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting up")
    # e.g. Connect to DB, initialize resources
    yield
    print("App shutting down")
    # e.g. Close DB connection, cleanup


app = FastAPI(lifespan=lifespan)

router = APIRouter()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(employee.router, prefix="/employee", tags=["employee"])
    
