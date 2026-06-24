from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from database import connect_db, close_db
from auth import router as auth_router
from questions import router as questions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: test DB connection. Shutdown: close connection."""
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Similar Question Finder API",
    description="EdTech backend for finding semantically similar questions using embeddings.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — supports wildcard "*" or a specific frontend URL from .env
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

if frontend_url == "*":
    # Allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_url, "http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(questions_router, prefix="/questions", tags=["Questions"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint — confirms the API is live."""
    return {"status": "ok", "message": "Similar Question Finder API is running."}


@app.get("/health", tags=["Health"])
async def health_check():
    """Health-check endpoint for monitoring and load balancers."""
    return {"status": "healthy"}
